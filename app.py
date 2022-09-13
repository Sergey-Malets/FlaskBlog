from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __repr__(self):  # припомощи этого метода, когда мы будем выбирать какой-либо объект класса Артикль, то будет
        # выдаваться сам объект, который предсатвляет из себя определённую запись в базе данных, а также будет выдаваться его id.
        return '<Article %r' % self.id

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(100),nullable=True)

    def __repr__(self):
        return f"<category {self.id}>"



class Users(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>" #определяет способ отображения класса в консоли, с его помощью выводим класс в формате Users и далее текущий id
    #метод записан для удобства и к функционированию таблиц не имеет отношения

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer)
    city = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<profiles {self.id}>"


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    profiles = Profiles.query.order_by(-Profiles.id).all()
    return render_template('about.html', profiles=profiles)

@app.route('/create_article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']


        article = Article(title=title, intro=intro, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'При добавлении статьи произошла ошибка'
    else:
        return render_template('create_article.html')

@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date).all()
    return render_template('posts.html', articles=articles)


@app.route('/my_template')
def my_template():
    return render_template('my_template.html')


@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return "User page: " + name + '-' + str(id)

@app.route("/register", methods=('POST','GET'))
def register():
    if request.method == "POST":
        #здесь должна быть проверка корректности введенных данных
        try:
            hash = generate_password_hash(request.form['psw'])
            u = Users(email=request.form['email'], psw=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=request.form['name'], old=request.form['old'],
                         city=request.form['city'], user_id = u.id)
            db.session.add(p)
            db.session.commit()# именно этот метод физически меняет файл БД и сохраняет изменения в таблицах
        except:
            db.session.rollback()# откатка в состояние как будто ничего не добавлялось
            print("ошибка добавления в БД")
        return redirect(url_for('about'))

    return render_template('register.html', title = "Регистрация")




if __name__ == '__main__':
    app.run(debug=True)
