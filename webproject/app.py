from datetime import datetime
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .models import db, User, Book, Rental, Comment
import os
from .forms import RegistrationForm, LoginForm

app = Flask(__name__)
migrate = Migrate(app, db)

basedir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basedir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = 'dev'

# ORM
db.init_app(app)
migrate.init_app(app, db)


@app.route('/')
def welcome():
    return render_template('welcome.html')


# SIGNUP
@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():

        user = User.query.filter_by(useremail=form.email.data).first()
        if user:
            flash("이미 존재하는 회원입니다")
        else:
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password.data),
                        useremail=form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


# sLOGIN
@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():

        error = None

        user = User.query.filter_by(useremail=form.email.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        flash(error)

        if error is None:
            session.clear()
            session['isLogin'] = True
            session['user_id'] = user.id
            return render_template('loggedin.html')
    return render_template('login.html', form=form)


# LOGOUT
@app.route('/logout')
def logout():
    try:
        if session['isLogin']:
            session.clear()
            return render_template('welcome.html')
    except:
        return redirect(url_for('login'))


# GETBOOK
@app.route("/getbook")
def getBook():
    try:
        if session['isLogin']:
            page = request.args.get('page', type=int, default=1)
            books = Book.query.paginate(page, per_page=8)
            return render_template('book.html', books=books)
    except:
        return redirect(url_for('login'))


@app.route("/rental", methods=('POST', 'GET'))
def rentalBook():
    try:
        if session['isLogin']:
            bookid = request.form.get("book_id")
            book = Book.query.filter(Book.id == bookid).first()
            userid = session['user_id']

            error = ""

            # 이미 대여한거는 여기에 추가하면 될듯?
            rental_already = Rental.query.filter(Rental.user_id == userid, Rental.book_id == bookid, Rental.return_date == None).first()
            if book.stock <= 0:
                error = "현재 대여가 불가능합니다"
            elif rental_already:
                error = "이미 대여한 책입니다."
            elif book.stock > 0:
                new_rental = Rental(user_id=userid, book_id=bookid)
                book.stock -= 1
                db.session.add(new_rental)
                db.session.commit()
            flash(error)

            return redirect(url_for('getBook'))
    except:
        return redirect(url_for('login'))


@app.route("/return", methods=('POST', 'GET'))
def returnBook():
    try:
        if session['isLogin']:
            userid = session['user_id']

            if request.method == 'POST':

                rentalid = request.form.get('rentalid')
                rental = Rental.query.filter(Rental.id == rentalid).first()
                rental.return_date = datetime.today()
                rental.book.stock += 1
                db.session.commit()

            rentals = Rental.query.filter(Rental.user_id == userid, Rental.return_date == None).all()

            return render_template('return.html', rentals=rentals)

    except:
        return redirect(url_for('login'))


@app.route('/log')
def rentLog():
    try:
        if session['isLogin']:
            userid = session['user_id']
            rentals = Rental.query.filter(Rental.user_id == userid).all()

            return render_template('rent_log.html', rentals=rentals)

    except:
        return redirect(url_for('login'))


@app.route('/<int:book_id>')
def getBookDetail(book_id):
    try:
        if session['isLogin']:
            book = Book.query.filter_by(id=book_id).first()
            comments = Comment.query.filter(Comment.book_id == book_id).order_by(Comment.date.desc()).all()

            return render_template('book_detail.html', book=book, comments=comments)
    except:
        return redirect(url_for('login'))


@app.route('/<int:book_id>/comment', methods=["POST"])
def create_comment(book_id):
    try:
        if session['isLogin']:
            userid = session['user_id']

            if request.method == "POST":

                content = request.form.get('content')
                rating = request.values.get('rating')
                comment = Comment(user_id=userid, content=content, book_id=book_id, rating=rating)
                db.session.add(comment)
                db.session.commit()
                ratings = Comment.query.filter(Comment.book_id == book_id, Comment.rating != None).all()

                sum_rating = 0
                for rating in ratings:
                    sum_rating += rating.rating

                avg_rating = round(sum_rating/len(ratings))
                book = Book.query.get(book_id)
                book.rating = avg_rating

                db.session.commit()

            return redirect(url_for('getBook', book_id=book_id))
    except:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()