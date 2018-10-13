import os
import tempfile
from textwrap import dedent

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from flask_filealchemy import FileAlchemy, LoadError


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return SQLAlchemy(app)


def test_load_single_table(db):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    with tempfile.TemporaryDirectory() as data_dir:
        authors_dir = os.path.join(data_dir, 'authors')
        max_mustermann = os.path.join(authors_dir, 'max-mustermann.yml')
        erika_mustermann = os.path.join(authors_dir, 'erika-mustermann.yml')

        os.mkdir(authors_dir)

        with open(max_mustermann, 'w') as fd:
            fd.write(dedent('''
                slug: max-mustermann
                name: Max Mustermann
            '''))

        with open(erika_mustermann, 'w') as fd:
            fd.write(dedent('''
                slug: erika-mustermann
                name: Erika Mustermann
            '''))

        db.app.config['FILEALCHEMY_MODELS'] = (Author,)
        db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir

        FileAlchemy(app, db).load_tables()

        assert Author.query.count() == 2

        os.remove(max_mustermann)
        os.remove(erika_mustermann)
        os.rmdir(authors_dir)


def test_invalid_data(db):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    with tempfile.TemporaryDirectory() as data_dir:
        authors_dir = os.path.join(data_dir, 'authors')
        invalid = os.path.join(authors_dir, 'invalid.yml')

        os.mkdir(authors_dir)

        for data in ('invalid', '[1, 2, 3]', 'key: value'):
            with open(invalid, 'w') as fd:
                fd.write(data)

            db.app.config['FILEALCHEMY_MODELS'] = (Author,)
            db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir

            with pytest.raises(LoadError):
                FileAlchemy(app, db).load_tables()

        os.remove(invalid)
        os.rmdir(authors_dir)


def test_foreign_keys(db):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    class Book(db.Model):
        __tablename__ = 'books'

        slug = Column(String(255), primary_key=True)
        title = Column(String(255), nullable=False)
        author_slug = Column(String(255), ForeignKey('authors.slug'),
                             nullable=False)
        contents = Column(Text, default=None)

        author = relationship('Author', backref='books')

    with tempfile.TemporaryDirectory() as data_dir:
        authors_dir = os.path.join(data_dir, 'authors')
        books_dir = os.path.join(data_dir, 'books')

        author = os.path.join(authors_dir, 'author.yml')
        first_book = os.path.join(books_dir, 'first-book.yml')
        second_book = os.path.join(books_dir, 'second-book.yml')

        os.mkdir(authors_dir)
        os.mkdir(books_dir)

        with open(author, 'w') as fd:
            fd.write(dedent('''
                slug: max-mustermann
                name: Max Mustermann
            '''))

        with open(first_book, 'w') as fd:
            fd.write(dedent('''
                slug: first-book
                title: First Book
                author_slug: max-mustermann
                contents: |
                    First line.
                    Second line.
            '''))

        with open(second_book, 'w') as fd:
            fd.write(dedent('''
                slug: second-book
                title: Second Book
                author_slug: max-mustermann
                contents: |
                    First line.
                    Second line.
            '''))

        db.app.config['FILEALCHEMY_MODELS'] = (Author, Book,)
        db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir

        FileAlchemy(app, db).load_tables()

        assert Author.query.count() == 1
        assert Book.query.count() == 2

        os.remove(first_book)
        os.remove(second_book)
        os.remove(author)
        os.rmdir(authors_dir)
        os.rmdir(books_dir)
