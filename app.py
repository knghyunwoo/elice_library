import pymysql
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
api = Api(app)

# #데이터베이스 연결
conn = pymysql.connect( 
        user='root', 
        passwd='Iamjenius1', 
        host='127.0.0.1', 
        db='library', 
        charset='utf8'
    )
curs = conn.cursor()

# parser = reqparse.RequestParser()

#완전 기본루트 환영루트
@app.route('/')
def welcome():
    return render_template('welcome.html')

# session을 위한 secret_key 설정
app.config.from_mapping(SECRET_KEY='dev')

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
        # 이미 있는 계정이라면?
        elif curs.execute(
            'SELECT idEmail FROM user WHERE idEmail = ?', (username,)
        ).fetchone() is not None:
            error = f"{username} 계정은 이미 등록된 계정입니다."
        # username_tuple = (username, )
        # query = f"SELECT idEmail FROM user WHERE idEmail = {username_tuple}"
        # print(curs.execute(query).fetchone())
        # if curs.execute(query).fetchone() is not None:
        #     error = '계정은 이미 등록된 계정입니다.'

        # 에러 메세지를 화면에 나타냅니다. (flashing)
        flash(error)

        # 에러가 발생하지 않았다면 회원가입 실행
        if error is None:
            insert_value = (username, generate_password_hash(password), name)
            query = f"INSERT INTO user (idEmail, password, name) VALUES {insert_value}"
            curs.execute(query)
            conn.commit()
            return redirect(url_for('login'))


    return render_template('register.html')

#LOGIN
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        sql = "SELECT * FROM user WHERE idEmail = (%s)"
        curs.execute(sql, (username))
        user = curs.fetchone()

        print(user)

        # 입력한 유저의 정보가 없을 때
        if user is None:
            error = '등록되지 않은 계정입니다.'
        elif not check_password_hash(user[1], password): #3번째 인덱스가 비밀번호입니다.
            error = 'password가 틀렸습니다.'
        
        # 정상적인 정보를 요청받았다면?
        if error is None:
            # 로그인을 위해 기존 session을 비웁니다.
            session.clear()
            # 지금 로그인한 유저의 정보로 session을 등록합니다.
            session['user_id'] = user[0] #0번째 인덱스가 user_id 값입니다.
            
            return render_template('loggedin.html')
        
        return error

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