from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, regexp
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):

    email = EmailField('이메일', validators=[DataRequired(message='빈칸을 채워주세요'),
            Length(min=6, max=30), Email(message='이메일형태가 아닙니다')])
    password = PasswordField('비밀번호', validators=[DataRequired(message='빈칸을 채워주세요'),
            Length(min=8, message='최소 8자리로 해주세요'), EqualTo('password_check', '비밀번호가 일치하지 않습니다'),
            regexp('^(?=.*[a-zA-Z])(?=.*[!@#$%^~*+=-])(?=.*[0-9]).{8,20}$', message = '특수문자와 숫자를 넣어주세요')])
    password_check = PasswordField('비밀번호 확인', validators=[DataRequired(message='빈칸을 채워주세요')])
    username = StringField('사용자 이름', validators=[DataRequired(message='빈칸을 채워주세요'),
                Length(min=2, max=25, message='길이는 2-25자로 해주세요'),
                regexp(regex='^[가-힣a-zA-Z]+$', message='한국어나 영어로만 써주세요')])

class SuperRegistrationForm(FlaskForm):

    email = EmailField('이메일', validators=[DataRequired(message='빈칸을 채워주세요'),
            Length(min=6, max=30), Email(message='이메일형태가 아닙니다')])
    password = PasswordField('비밀번호', validators=[DataRequired(message='빈칸을 채워주세요'),
            Length(min=8, message='최소 8자리로 해주세요'), EqualTo('password_check', '비밀번호가 일치하지 않습니다'),
            regexp('^(?=.*[a-zA-Z])(?=.*[!@#$%^~*+=-])(?=.*[0-9]).{8,20}$', message = '특수문자와 숫자를 넣어주세요')])
    password_check = PasswordField('비밀번호 확인', validators=[DataRequired(message='빈칸을 채워주세요')])
    username = StringField('사용자 이름', validators=[DataRequired(message='빈칸을 채워주세요'),
                Length(min=2, max=25, message='길이는 2-25자로 해주세요'),
                regexp(regex='^[가-힣a-zA-Z]+$', message='한국어나 영어로만 써주세요')])
    super = PasswordField('관리자 비밀번호', validators=[DataRequired(message='빈칸을 채워주세요')])


class LoginForm(FlaskForm):

    email = EmailField('이메일', validators=[DataRequired(message='빈칸을 채워주세요'),
            Email(message='이메일형태가 아닙니다')])
    password = PasswordField('비밀번호', validators=[DataRequired(message='빈칸을 채워주세요'),
                regexp('^(?=.*[a-zA-Z])(?=.*[!@#$%^~*+=-])(?=.*[0-9]).{8,20}$', message = '특수문자와 숫자를 넣어주세요')]) 
