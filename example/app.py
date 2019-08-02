import os

from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from flask_filealchemy import FileAlchemy


app = Flask(__name__)

# configure Flask-SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = 'authors'

    slug = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)


class Book(db.Model):
    __tablename__ = 'books'

    slug = Column(String(255), primary_key=True)
    title = Column(String(255), nullable=False)
    author_slug = Column(
        String(255), ForeignKey('authors.slug'), nullable=False
    )
    bestseller = Column(Boolean, server_default='false')
    contents = Column(Text, default=None)

    author = relationship('Author', backref='books')


# configure Flask-FileAlchemy

app.config['FILEALCHEMY_DATA_DIR'] = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'data'
)
app.config['FILEALCHEMY_MODELS'] = (Author, Book)

FileAlchemy(app, db).load_tables()


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/authors/<slug>')
def author(slug):
    author = Author.query.filter(Author.slug == slug).first()

    if not author:
        abort(404)

    return author.name


@app.route('/books/<slug>')
def book(slug):
    book = Book.query.filter(Book.slug == slug).first()

    if not book:
        abort(404)

    return book.contents
