from datetime import date
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .models import db, User, Book, Rental, Comment
from .forms import RegistrationForm, LoginForm, SuperRegistrationForm
import os
import random

# export FLASK_ENV=development; export FLASK_APP=webproject.app

app = Flask(__name__)
migrate = Migrate(app, db)

basedir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basedir, 'db.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = 'dev'

wisesaying = ["양서는 처음 읽을 때는 새 친구를 얻은 것 같고, 전에 정독한 책을 다시 읽을 때는 옛 친구를 만나는 것 같다. - 골드 스미스",
"책 없는 방은 영혼 없는 육체와 같다. - 키케로", "내가 세계를 알게 된 것은 책에 의해서였다. - 사르트르", "책은 인생의 험준한 바다를 항해하는데 도움이 되게 남들이 마련해 준 나침반이요, 망원경이고 육분의고 도표이다. - 제시 리 베넷",
"약으로 병을 고치듯이 독서로 마음을 다스린다. - 카이사르", "독서는 완성된 사람을 만들고, 담론은 재치있는 사람을 만들며, 필기는 정확한 사람을 만든다. - 베이컨", "남의 책을 읽는 것에 시간을 보내라. 남이 고생한 것에 의해서 자신을 쉽게 개선할 수 있다. - 소크라테스",
"언제든 괴로운 환상을 위로하고자 한다면 너의 책으로 달려가라. 책은 언제나 변함없는 친절로 너를 대한다. - 풀러", "내가 인생을 안 것은 사람과 접촉했기 때문이 아니라 책과 접촉했었기 때문이다. - 아나톨 프랑스",
"모든 양서를 읽는 것은 지난 몇 세기 동안 걸친 가장 훌륭한 사람들과 대화 하는 것과 같다. - 데카르트", " 책을 사느라 들인 돈은 결코 손해가 아니다. 오히려 훗날에 만 배의 이익을 얻게 될 것이다. - 왕안석",
"오늘의 나를 있게 한 것은 우리 마을의 도서관이었다. 하버드 졸업자보다도 소중한 것이 독서하는 습관이다. - 빌 게이츠", "책 속에는 과거의 모든 영혼이 가로누워 있다. - 칼라일",
"한 시간 정도 독서하면 어떤 고통도 진정된다. - 몽테스키외", "책이란 넓디넓은 시간의 바다를 지나가는 배이다. - 프랜시스 베이컨", "과학에서는 최신의 연구서를 읽으라. 문학에서는 최고(古)의 책을 읽으라. 고전은 늘 새로운 것이다. - 리턴",
"인생은 매우 짧고 그 중 조용한 시간은 얼마 안 되므로 그 시간을 가치없는 책을 읽는데 낭비하지 말아야 한다. - 존 러스킨", "친구를 고르는 것처럼 저자를 고르라. - 로스코몬",
"단 한 권의 책 밖에 읽은 적이 없는 사람을 경계하라. - 디즈레일리", "당신에게 가장 필요한 책은 당신으로 하여금 가장 많이 생각하게 만드는 책이다. - 마크 트웨인",
"때로 독서란 독자를 가르친다기보다 머리를 도리어 산만하게 한다. 덮어놓고 많은 책을 읽는 것보다 몇몇 좋은 저자의 책을 골라 읽는 편이 훨씬 더 유익하다. - 톨스토이",
"먼저 유익하고 좋은 책을 읽어라. 그렇지 않으면 나중에 그 책을 읽을 시간이 없을런지도 모른다. - 헨리 소로", "책에도 볼 책이 있고 안 볼 책이 있다. - 한국속담",
"책과 친구는 수가 적고 좋아야 한다. - 스페인 속담", "고전이란 누구나 읽은 것으로 자부하려고 들지만 실은 누구나 읽고 싶어하지는 않는다. - 마크 트웨인",
"보기 드문 지식인을 만났을 때는 그가 어떤 책을 읽는가를 물어보아야 한다. - 에머슨", "좋은 내용이 많이 쓰여 있다고 해서 꼭 양서인 것은 아니다. - 세르반테스",
"나쁜 독서는 나쁜 교제보다 더 위험하다. - 힐티", "잡서의 난독은 일시적으로 다소의 이익을 줄지 모르나 궁극적으로는 시간과 정력의 낭비로 돌아간다. - 마틴",
"유익한 책이란 독자에게 포착(捕捉)을 요구하지 않고 못 배기게 하는 책이다. - 볼테르"
]

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
                        useremail=form.email.data, super=0)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

# SUPERSIGNUP
@app.route('/superregister', methods=('GET', 'POST'))
def superregister():
    form = SuperRegistrationForm()

    if request.method == 'POST' and form.validate_on_submit():

        user = User.query.filter_by(useremail=form.email.data).first()
        if user:
            flash("이미 존재하는 회원입니다")
        else:
            if form.super.data == "1234":
                user = User(username=form.username.data,
                            password=generate_password_hash(form.password.data),
                            useremail=form.email.data, super=1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                flash("관리자 비밀번호가 틀렸습니다")

    return render_template('superregister.html', form=form)

# LOGIN
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

        if error:
            return render_template('login.html', form=form)

        session.clear()
        session['isLogin'] = True
        session['user_id'] = user.id
        
        if user.super:
            return render_template('superloggedin.html')
        return render_template('loggedin.html')
    
    return render_template('login.html', form=form)


@app.route('/superLoggedin')
def superLoggedin():
    try:
        if session['isLogin']:
            userid = session['user_id']
            curuser = User.query.filter(User.id == userid).first()
            if curuser.super:
                return render_template('superloggedin.html')
            else:
                return render_template('loggedin.html')
    except:
        return redirect(url_for('login'))


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
            userid = session['user_id']
            page = request.args.get('page', type=int, default=1)
            curuser = User.query.filter(User.id == userid).first()
            if curuser.super:
                books = Book.query.paginate(page, per_page=8)
                return render_template('super_book.html', books=books)
            page = request.args.get('page', type=int, default=1)
            books = Book.query.paginate(page, per_page=8)
            return render_template('book.html', books=books)
    except:
        return redirect(url_for('login'))

@app.route("/plusstock", methods=('POST', 'GET'))
def plusBook():
    try:
        if session['isLogin']:
            userid = session['user_id']
            curuser = User.query.filter(User.id == userid).first()
            if curuser.super:
                bookid = request.form.get("book_id")
                book = Book.query.filter(Book.id == bookid).first()
                book.stock += 1
                db.session.commit()
            return redirect(url_for('getBook'))
    except:
        return redirect(url_for('login'))


@app.route("/minusstock", methods=('POST', 'GET'))
def minusBook():
    try:
        if session['isLogin']:
            userid = session['user_id']
            curuser = User.query.filter(User.id == userid).first()
            if curuser.super:
                bookid = request.form.get("book_id")
                book = Book.query.filter(Book.id == bookid).first()
                book.stock -= 1
                db.session.commit()
            return redirect(url_for('getBook'))
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
                rental.return_date = date.today()
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

@app.route('/superlog')
def superLog():
    try:
        if session['isLogin']:
            userid = session['user_id']
            curuser = User.query.filter(User.id == userid).first()
            if curuser.super:
                rentals = Rental.query.filter().all()
                return render_template('superlog.html', rentals=rentals)
    except:
        return redirect(url_for('login'))


@app.route('/<int:book_id>')
def getBookDetail(book_id):
    try:
        if session['isLogin']:
            book = Book.query.filter_by(id=book_id).first()
            comments = Comment.query.filter(Comment.book_id == book_id).order_by(Comment.date.desc()).all()
            saying = wisesaying[random.randint(0,30)]
            return render_template('book_detail.html', book=book, comments=comments, saying=saying)
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