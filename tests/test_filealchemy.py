import os
import tempfile
from textwrap import dedent

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String

from flask_filealchemy import FileAlchemy


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
