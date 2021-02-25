from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model) :
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    useremail = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Book(db.Model) :
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    publisher = db.Column(db.String(120), unique=True, nullable=False)
    author = db.Column(db.String(120), unique=True, nullable=False)
    published_at = db.Column(db.String(120), unique=True, nullable=False)
    page_count = db.Column(db.Integer, unique=True, nullable=False)
    isbn = db.Column(db.Integer, unique=True, nullable=False)
    description = db.Column(db.String(300), unique=True, nullable=False)
    link = db.Column(db.String(300), unique=True, nullable=False)
    image_path = db.Column(db.String(300), unique=True, nullable=False)
    stock= db.Column(db.Integer)
    rating= db.Column(db.Integer)
