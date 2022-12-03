from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def db(app):
    sqlalchemy = SQLAlchemy()

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    sqlalchemy.init_app(app)

    return sqlalchemy
