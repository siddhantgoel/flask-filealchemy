import os

from flask import Flask, abort
from sqlalchemy import Boolean, Column, ForeignKey, String

from flask_filealchemy import DeclarativeBase, FileAlchemy


class Author(DeclarativeBase):
    __tablename__ = 'authors'

    slug = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)


class Book(DeclarativeBase):
    __tablename__ = 'books'

    slug = Column(String(255), primary_key=True)
    title = Column(String(255), nullable=False)
    author_slug = Column(String(255), ForeignKey('authors.slug'),
                         nullable=False)
    bestseller = Column(Boolean, server_default='false')


app = Flask(__name__)
app.config['FILEALCHEMY_DATA_DIR'] = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'data'
)

file_alchemy = FileAlchemy(app)
file_alchemy.register_model(Author)
file_alchemy.register_model(Book)
file_alchemy.load_data()


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/authors/<slug>')
def author(slug):
    with file_alchemy.make_session() as session:
        author = session.query(Author).filter(Author.slug == slug).first()

        if not author:
            abort(404)

        return author.name


@app.route('/books/<slug>')
def book(slug):
    with file_alchemy.make_session() as session:
        book = session.query(Book).filter(Book.slug == slug).first()

        if not book:
            abort(404)

        return book
