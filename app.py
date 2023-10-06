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
    name = db.Column(db.String(100), primary_key=False)
    index = db.Column(db.String(100), primary_key=False, default='')
    quantity = db.Column(db.Integer)
    cost = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index_sal = db.Column(db.Integer, primary_key=False)
    sum_sal = db.Column(db.Integer, primary_key=False)
    name_sal = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Income %r>' % self.id


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


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
            return redirect('/')
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
            return redirect('/')
        except:
            return 'ПЫри добавление дохода произошла ошибка'

    else:
        return render_template("income.html")


if __name__ == "__main__":
    app.run(debug=True)
