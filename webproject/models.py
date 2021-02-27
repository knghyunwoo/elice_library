from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model) :
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    useremail = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=False, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Book(db.Model) :
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    publisher = db.Column(db.String(120), unique=False, nullable=False)
    author = db.Column(db.String(120), unique=False, nullable=False)
    published_at = db.Column(db.String(120), unique=False, nullable=False)
    page_count = db.Column(db.Integer, unique=False, nullable=False)
    isbn = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(300), unique=False, nullable=False)
    image_path = db.Column(db.String(300), unique=True, nullable=False)
    stock= db.Column(db.Integer)
    rating= db.Column(db.Integer)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.String(50), db.ForeignKey('book.id'), nullable=False) 
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'), nullable=False)
    book = db.relationship('Book')
    rent_date = db.Column(db.DateTime, nullable=False, default=datetime.today().date())
    return_date = db.Column(db.DateTime, nullable=True, default=None)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship('User')
    content = db.Column(db.TEXT)
    rating = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.today().date())



