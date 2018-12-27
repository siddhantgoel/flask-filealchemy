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


def test_invalid_directory(db):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    db.app.config['FILEALCHEMY_MODELS'] = (Author,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = '/does/not/exist/'

    with pytest.raises(LoadError):
        FileAlchemy(app, db).load_tables()


def test_load_single_table(db, tmpdir):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    data_dir = tmpdir.mkdir('data_dir')

    authors_dir = data_dir.mkdir('authors')
    max_mustermann = authors_dir.join('max-mustermann.yml')
    erika_mustermann = authors_dir.join('erika-mustermann.yml')

    max_mustermann.write(
        dedent(
            '''
            slug: max-mustermann
            name: Max Mustermann
            '''
        )
    )

    erika_mustermann.write(
        dedent(
            '''
            slug: erika-mustermann
            name: Erika Mustermann
            '''
        )
    )

    db.app.config['FILEALCHEMY_MODELS'] = (Author,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = str(data_dir)

    FileAlchemy(app, db).load_tables()

    assert Author.query.count() == 2


def test_invalid_data(db, tmpdir):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    data_dir = tmpdir.mkdir('data_dir')

    authors_dir = data_dir.mkdir('authors')
    invalid = authors_dir.join('invalid.yml')

    for data in ('invalid', '[1, 2, 3]', 'key: value'):
        invalid.write(data)

        db.app.config['FILEALCHEMY_MODELS'] = (Author,)
        db.app.config['FILEALCHEMY_DATA_DIR'] = str(data_dir)

        with pytest.raises(LoadError):
            FileAlchemy(app, db).load_tables()


def test_foreign_keys(db, tmpdir):
    app = db.get_app()

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
        contents = Column(Text, default=None)

        author = relationship('Author', backref='books')

    data_dir = tmpdir.mkdir('data_dir')

    authors_dir = data_dir.mkdir('authors')
    books_dir = data_dir.mkdir('books')

    author = authors_dir.join('author.yml')
    first_book = books_dir.join('first-book.yml')
    second_book = books_dir.join('second-book.yml')

    author.write(
        dedent(
            '''
            slug: max-mustermann
            name: Max Mustermann
            '''
        )
    )

    first_book.write(
        dedent(
            '''
            slug: first-book
            title: First Book
            author_slug: max-mustermann
            contents: |
                First line.
                Second line.
            '''
        )
    )

    second_book.write(
        dedent(
            '''
            slug: second-book
            title: Second Book
            author_slug: max-mustermann
            contents: |
                First line.
                Second line.
            '''
        )
    )

    db.app.config['FILEALCHEMY_MODELS'] = (Author, Book)
    db.app.config['FILEALCHEMY_DATA_DIR'] = str(data_dir)

    FileAlchemy(app, db).load_tables()

    assert Author.query.count() == 1
    assert Book.query.count() == 2


def test_load_from_all_file(db, tmpdir):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    data_dir = tmpdir.mkdir('data_dir')

    authors_dir = data_dir.mkdir('authors')
    all_ = authors_dir.join('_all.yml')

    all_.write(
        dedent(
            '''
            - slug: max-mustermann
              name: Max Mustermann
            - slug: erika-mustermann
              name: Erika Mustermann
            '''
        )
    )

    db.app.config['FILEALCHEMY_MODELS'] = (Author,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = str(data_dir)

    FileAlchemy(app, db).load_tables()

    assert Author.query.count() == 2
