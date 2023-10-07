from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
db = SQLAlchemy(app)


# init database
# from app import app, db
# app.app_context().push()
# db.create_all()


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), primary_key=False, default='Не указана покупка')
    index = db.Column(db.String(100), primary_key=False, default='')
    quantity = db.Column(db.Integer, default=1)
    cost = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Article %r>' % self.id


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index_sal = db.Column(db.Integer, primary_key=False, default=0)
    sum_sal = db.Column(db.Integer, primary_key=False, default=0)
    name_sal = db.Column(db.String(100), default='Не указано описание')
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Income %r>' % self.id


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/about')
def about_posts():
    sum_articles = 0
    sum_articles_for_today = 0
    sum_articles_for_week = 0
    sum_articles_for_month = 0
    sum_articles_for_year = 0
    sum_income = 0
    sum_incomes_for_today = 0
    sum_incomes_for_week = 0
    sum_incomes_for_month = 0
    sum_incomes_for_year = 0
    for_date = ''
    cost = 0
    x = 0

    to_day = datetime.today().date()
    a = ''
    articles = Article.query.order_by(Article.date.desc()).all()
    # Расходы
    for e in articles:

        cost = e.cost
        x = e.quantity
        sum_articles += x * cost
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
# Доходы
    income = Income.query.order_by(Income.date.desc()).all()
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
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


@app.route('/incomes')
def posts2():
    income = Income.query.order_by(Income.date.desc()).all()
    return render_template("incomes.html", income=income)


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == 'POST':

        name = request.form['name']
        index = request.form['index']
        quantity = request.form['quantity']
        cost = request.form['cost']

        article = Article(name=name, index=index, quantity=quantity, cost=cost)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/create-article')
        except:
            return 'ПЫри добавление расходов произошла ошибка'

    else:
        return render_template("create-article.html")


@app.route('/income', methods=['POST', 'GET'])
def income1():
    if request.method == 'POST':
        index_sal = request.form['index_sal']
        sum_sal = request.form['sum_sal']
        name_sal = request.form['name_sal']

        income = Income(index_sal=index_sal, sum_sal=sum_sal, name_sal=name_sal)

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
