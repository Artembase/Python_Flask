from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user
from flask_login import UserMixin
import flask_login

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


# init database
# from app import app, db
# app.app_context().push()
# db.create_all()

# @login_manager.user_loader
# def load_user(user_id):
#     print(Registration.query.get(int(user_id)) + ' djn nfrjt')
#     return Registration.query.get(int(user_id))
@login_manager.user_loader
def load_user(user_id):
    return Registration.query.filter(Registration.id == user_id).first()


@login_manager.unauthorized_handler
def handle_needs_login():
    return redirect(url_for('login'))


class Registration(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Registration %r>' % self.id


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), primary_key=False, default='Не указана покупка')
    index = db.Column(db.String(100), primary_key=False, default='')
    quantity = db.Column(db.Integer, default=1)
    cost = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('registration.id'))
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Article %r>' % self.id


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index_sal = db.Column(db.Integer, primary_key=False, default=0)
    sum_sal = db.Column(db.Integer, primary_key=False, default=0)
    name_sal = db.Column(db.String(100), default='Не указано описание')
    user_id = db.Column(db.Integer, db.ForeignKey('registration.id'))
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Income %r>' % self.id


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        # проверка коректности

        try:
            hash1 = generate_password_hash(request.form['psw'])
            u = Registration(email=request.form['email'], psw=hash1)
            db.session.add(u)
            db.session.commit()
            return redirect('/registration')
        except:
            return 'Неправильно введен пароль или такой ник уже занят'
    return render_template("registration.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("index.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email_login = request.form['email_login']
        psw_login = request.form['psw_login']
        registration = Registration.query.order_by(Registration.date.desc())

        for e in registration:
            db_email = e.email
            db_password = e.psw

            if email_login == db_email and check_password_hash(db_password, psw_login):
                user = Registration.query.filter_by(email=email_login).first()
                login_user(user)
                return render_template("index.html")
            # else:
            #     return 'Не правильно введен логин или пароль'
        # if email_login
    return render_template("login.html")


@app.route('/about')
@login_required
def about_posts():
    # return 'Current user is ' + current_user.email
    sum_articles = 0
    sum_articles_for_today = 0
    sum_articles_for_week = 0
    sum_articles_for_month = 0
    sum_articles_for_year = 0
    sum_income = 0
    sum_incomes_for_today = 0
    sum_incomes_for_week = 0
    sum_incomes_for_month = 0

    for_date = ''

    to_day = datetime.today().date()
    a = ''
    articles = Article.query.filter(Article.user_id == current_user.id).order_by(Article.date.desc()).all()
    # Расходы
    for e in articles:

        cost = e.cost
        x = e.quantity
        sum_articles = x * cost
        sum_articles_for_year += sum_articles
        for_date = e.date.date()
        # разница в днях между сегодня и дой из бд
        a = to_day - for_date
        a = a.days
        if a < 1:
            sum_articles_for_today += sum_articles
        elif a <= 7:
            sum_articles_for_week += sum_articles
        elif a <= 30:
            sum_articles_for_month += sum_articles

    sum_articles_for_week += sum_articles_for_today
    sum_articles_for_month += sum_articles_for_week
    # Доходы .filter(Income.index_sal == '123')
    income = Income.query.filter(Income.user_id == current_user.id).order_by(Income.date.desc()).all()
    for e in income:

        sum_income += e.sum_sal
        for_date = e.date.date()
        # разница в днях между сегодня и датой из бд
        a = to_day - for_date
        a = a.days
        if a < 1:
            sum_incomes_for_today += e.sum_sal
        elif a < 7:
            sum_incomes_for_week += e.sum_sal
        elif a < 30:
            sum_incomes_for_month += e.sum_sal

    sum_incomes_for_week += sum_incomes_for_today
    sum_incomes_for_month += sum_incomes_for_week

    return render_template("about.html", sum_articles=sum_articles,
                           sum_income=sum_income, for_date=for_date, to_day=to_day,
                           a=a, sum_articles_for_week=sum_articles_for_week,
                           sum_articles_for_month=sum_articles_for_month, sum_articles_for_today=sum_articles_for_today,
                           sum_incomes_for_today=sum_incomes_for_today, sum_incomes_for_week=sum_incomes_for_week,
                           sum_incomes_for_month=sum_incomes_for_month, sum_articles_for_year=sum_articles_for_year,
                           )


@app.route('/posts')
@login_required
def posts():
    articles = Article.query.filter(Article.user_id == current_user.id).order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


# @login_manager.user_loader
@app.route('/incomes')
@login_required
def posts2():
    income = Income.query.filter(Income.user_id == current_user.id).order_by(Income.date.desc()).all()
    return render_template("incomes.html", income=income)


@app.route('/delete/<int:id>/outcome', methods=['POST', 'GET'])
def delete_outcome(id):
    article = Article.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'ПЫри удалении произошла ошибка'


@app.route('/delete/<int:id>/income', methods=['POST', 'GET'])
def delete_income(id):
    income = Income.query.get_or_404(id)
    try:
        db.session.delete(income)
        db.session.commit()
        return redirect('/incomes')
    except:
        return 'ПЫри удалении произошла ошибка'


@app.route('/create-article', methods=['POST', 'GET'])
@login_required
def create_article():
    if request.method == 'POST':

        name = request.form['name']
        index = request.form['index']
        quantity = request.form['quantity']
        cost = request.form['cost']

        article = Article(name=name, index=index, quantity=quantity, cost=cost, user_id=current_user.id)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/create-article')
        except:
            return 'ПЫри добавление расходов произошла ошибка'

    else:
        return render_template("create-article.html")


@app.route('/income', methods=['POST', 'GET'])
@login_required
def income1():
    if request.method == 'POST':
        index_sal = request.form['index_sal']
        sum_sal = request.form['sum_sal']
        name_sal = request.form['name_sal']

        income = Income(index_sal=index_sal, sum_sal=sum_sal, name_sal=name_sal, user_id=current_user.id)

        try:
            db.session.add(income)
            db.session.commit()
            return redirect('/income')
        except:
            return 'ПЫри добавление дохода произошла ошибка'

    else:
        return render_template("income.html")


if __name__ == "__main__":
    app.run(debug=True)
