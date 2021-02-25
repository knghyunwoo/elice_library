from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .models import db, User
from . import config
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
        username = request.form['username']
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

        # 에러 메세지를 화면에 나타냅니다. (flashing)
        flash(error)

        if error is None:
            insert_value = User(username=name, password=generate_password_hash(password), useremail=username)
            db.session.add(insert_value)
            db.session.commit()        
            return redirect(url_for('login'))

    return render_template('register.html')

#LOGIN
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
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
            return render_template('loggedin.html')

    return render_template('login.html')

#LOGOUT
@app.route('/logout')
def logout():
    try:
        session.clear()
        return render_template('welcome.html')
    except:
        return "logout failed"


if __name__ == "__main__":
    app.run()