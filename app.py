import pymysql
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_RESTful import reqparse, abort, Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
api = Api(app)

# #데이터베이스 연결, azure mysql로 데이터베이스를 설정하였습니다.
# db = pymysql.connect( 
#         user = 'knghyunwoo@elice-api',
#         passwd = 'iAMJENIUS1',
#         host = 'elice-api.mysql.database.azure.com',
#         db = 'elice_db',
#         charset = 'utf8'
#     )
# cursor = db.cursor()

parser = reqparse.RequestParser()

#완전 기본루트
@app.route('/')
def abc():
    return """
        If you want to 
        1. Signup, please add /auth/register
        2. Login, please add /auth/login
        3. Logout, please add /auth/logout    
    """

"""
과제 1
User APIs : 유저 SignUp / Login / Logout

SignUp API : *fullname*, *email*, *password* 을 입력받아 새로운 유저를 가입시킵니다.
Login API : *email*, *password* 를 입력받아 특정 유저로 로그인합니다.
Logout API : 현재 로그인 된 유저를 로그아웃합니다.
"""

# session을 위한 secret_key 설정
app.config.from_mapping(SECRET_KEY='dev')
#SIGNUP
@app.route('/auth/register', methods=['POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']        
        error = None

        # 아이디가 없다면?
        if not fullname:
            error = 'fullname이 유효하지 않습니다.'
        # 비밀번호가 없다면?
        elif not password:
            error = 'Password가 유효하지 않습니다.'
        # 이메일이 없다면?
        elif not email:
            error = 'email이 유효하지 않습니다.'

        # 에러가 발생하지 않았다면 회원가입 실행
        # if error is None:
        #     cursor.execute(
        #         'INSERT INTO `user` (`fullname`, `email`, `password`) VALUES (%s, %s, %s)',
        #         (fullname, email, generate_password_hash(password))
        #     )
        #     db.commit()

        return "Success You are now registered"

#LOGIN
@app.route('/auth/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        sql = "SELECT * FROM user WHERE email = (%s)"
        # cursor.execute(sql, (email))
        # user = cursor.fetchone()

        # print(user)

        # # 입력한 유저의 정보가 없을 때
        # if user is None:
        #     error = '등록되지 않은 계정입니다.'
        # elif not check_password_hash(user[3], password): #3번째 인덱스가 비밀번호입니다.
        #     error = 'password가 틀렸습니다.'

        # # 정상적인 정보를 요청받았다면?
        # if error is None:
        #     # 로그인을 위해 기존 session을 비웁니다.
        #     session.clear()
        #     # 지금 로그인한 유저의 정보로 session을 등록합니다.
        #     session['user_id'] = user[0] #0번째 인덱스가 user_id 값입니다.
            
        #     return "Success You are now logged in"
        
        return error

#LOGOUT
@app.route('/auth/logout')
def logout():
    try:
        session.clear()
        return "logout success"
    except:
        return "logout failed"


if __name__ == "__main__":
    app.run()