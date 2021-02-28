from datetime import datetime
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .models import db, User, Book, Rental, Comment
import os

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


#완전 기본루트 환영루트
@app.route('/')
def welcome():
    return render_template('welcome.html')

#SIGNUP
# /register 주소에서 GET과 POST 메소드 방식의 요청을 모두 받음
@app.route('/register', methods=('GET', 'POST'))
def register():
    # POST 요청을 받았다면?
    if request.method == 'POST':
        # 아이디와 비밀번호를 폼에서 가져옵니다.
        name = request.form['name']
        username = request.form['email']
        password = request.form['password']
        password_check = request.form['password_check']

        error = None
        
        # 이름이 없다면?
        if not name:
            error = '이름이 유효하지 않습니다.'
        # 아이디가 없다면?
        elif not username:
            error = '아이디가 유효하지 않습니다.'
        # 비밀번호가 없다면?
        elif not password:
            error = '비밀번호가 유효하지 않습니다.'
        elif password != password_check:
            error = "비밀번호가 비밀번호 확인과 같지 않습니다."

        user = User.query.filter_by(username=username).first()
        if user:
            error = "이미 존재하는 회원입니다"

        # 에러 메세지를 화면에 나타냅니다. (flashing)
        flash(error)

        if error is None:
            insert_value = User(useremail=username, username=name, password=generate_password_hash(password))
            db.session.add(insert_value)
            db.session.commit()        
            return redirect(url_for('login'))

    return render_template('register.html')

#LOGIN
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        error = None
            
        user = User.query.filter_by(username=username).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, password):
            error = "비밀번호가 올바르지 않습니다."

        flash(error)

        if error is None:
            session.clear()
            session['isLogin'] = True
            session['user_id'] = user.id
            return render_template('loggedin.html')

    return render_template('login.html')

#LOGOUT
@app.route('/logout')
def logout():
    if session['isLogin'] != True:
        return render_template('login.html')
    try:
        session.clear()
        return render_template('welcome.html')
    except:
        return "logout failed"

#GETBOOK
@app.route("/getbook")
def getBook():
    if session['isLogin'] != True:
        return render_template('login.html')
    
    books = Book.query.all()
    data = []

    for book in books:

        temp = {}
        temp['id'] = book.id
        temp['name'] = book.name
        temp['publisher'] = book.publisher
        temp['author'] = book.author
        temp['published_at'] = book.published_at
        temp['page_count'] = book.page_count
        temp['isbn'] = book.isbn
        temp['description'] = book.description
        temp['image_path'] = book.image_path
        temp['stock'] = book.stock
        temp['rating'] = book.rating

        data.append(temp)

    return render_template('book.html', books=data)

@app.route("/rental", methods=('POST', 'GET'))
def rentalBook():
    if session['isLogin'] != True:
        return render_template('login.html')
        
    bookid = request.form.get("book_id")
    book = Book.query.filter(Book.id == bookid).first()
    userid = session['user_id']

    error = ""

    if book.stock > 0:
        new_rental = Rental(user_id=userid, book_id=bookid)
        book.stock -= 1
        db.session.add(new_rental)
        db.session.commit()
    else:
        error = "현재 대여가 불가능합니다"

    flash(error)

    return redirect(url_for('getBook'))

@app.route("/return", methods=('POST', 'GET'))
def returnBook():
    if session['isLogin'] != True:
        return render_template('login.html')

    userid = session['user_id']

    if request.method == 'POST':

        rentalid = request.form.get('rentalid')
        rental = Rental.query.filter(Rental.id == rentalid).first()
        rental.return_date = datetime.today()

        book = Book.query.filter(Book.id == rental.book_id).first()
        book.stock += 1
        db.session.commit()

    rentals = Rental.query.filter(Rental.user_id == userid, Rental.return_date == None).all()

    return render_template('return.html', rentals = rentals)


@app.route('/log')
def rentLog():

    if session['isLogin'] != True:
        return render_template('login.html')

    userid = session['user_id']
    rentals = Rental.query.filter(Rental.user_id == userid).all()

    return render_template('rent_log.html', rentals = rentals)

@app.route('/<int:book_id>')
def getBookDetail(book_id):

    book = Book.query.filter_by(id=book_id).first()
    comments = Comment.query.filter(Comment.book_id == book_id).order_by(Comment.date.desc()).all()

    return render_template('book_detail.html', book=book, comments=comments)

@app.route('/<int:book_id>/comment', methods=["POST"])
def create_comment(book_id):

    userid = session['user_id']

    if request.method == "POST":

        content = request.form['content']
        rating = request.values.get('rating')
        comment = Comment(user_id=userid, content=content, book_id=book_id, rating = rating)
        db.session.add(comment)
        db.session.commit()

        ratings = Comment.query.filter(Comment.book_id == book_id, Comment.rating != None).all()

        sum_rating = 0
        for rating in ratings:
            sum_rating += rating.rating

        avg_rating = round(sum_rating/len(ratings), 1)
        book = Book.query.get(book_id)
        book.rating = avg_rating

        db.session.commit()

    return redirect(url_for('getBook',book_id=book_id))


if __name__ == "__main__":
    
    app.run()