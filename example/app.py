import os
from functools import partial

from flask import Flask, abort

from flask_filealchemy import FileAlchemy

from .models import Author, Book

app = Flask(__name__)
app.config['FILEALCHEMY_DATA_DIR'] = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'data'
)
app.config['FILEALCHEMY_MODELS'] = (Author, Book)

session = FileAlchemy(app)

not_found = partial(abort, 404)


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/authors/<slug>')
def author(slug):
    author = session.query(Author).filter(Author.slug == slug).first()

    if not author:
        not_found()

    return author.name


@app.route('/books/<slug>')
def book(slug):
    book = session.query(Book).filter(Book.slug == slug).first()

    if not book:
        not_found()

    return book
