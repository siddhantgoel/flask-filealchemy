Flask-FileAlchemy
=================

.. image:: https://badge.fury.io/py/flask-filealchemy.svg
    :target: https://pypi.python.org/pypi/flask-filealchemy

.. image:: https://travis-ci.org/siddhantgoel/flask-filealchemy.svg?branch=stable
    :target: https://travis-ci.org/siddhantgoel/flask-filealchemy

Flask-FileAlchemy lets you use YAML-formatted plain-text files as the data store
for your Flask_ app.

Background
----------

While there are better alternatives to use in production than plain-text (please
don't use plain-text in production), the constraints on applications that only
have to run locally are much more relaxed.

One very strong use case here is generating static sites. While `Frozen-Flask`_
lets you "freeze" an entire Flask application to a set of HTML files, you still
need to make some data available to your app in the first place. This means
setting up a data store (for instance SQLite). These data stores are good and do
the job extremely well, but it's hard to beat plain-text as a format for
entering data, especially when the environment is not production.

Plugging Flask-FileAlchemy in completes the loop by letting you enter your data
in plain text files, which `Flask-SQLAlchemy`_ can read, which is then available
to your Flask application, which Frozen-Flask can then freeze.

This lets you retain the comfort of dynamic sites without compromising on the
simplicity of static sites.

Installation
------------

Flask-FileAlchemy is not ready for prime time yet. I'll put it up on PyPI when
it's ready.

Usage
-----

Define your data models using `Flask-SQLAlchemy`_ like you normally would, and
then add your data in YML files inside the :code:`data/` directory.

.. code-block:: python

   app = Flask(__name__)

   # configure Flask-SQLAlchemy
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
   db = SQLAlchemy(app)

   class Author(db.Model):
       __tablename__ = 'authors'

       slug = Column(String(255), primary_key=True)
       name = Column(String(255), nullable=False)

   # configure Flask-FileAlchemy
   app.config['FILEALCHEMY_DATA_DIR'] = os.path.join(
       os.path.dirname(os.path.realpath(__file__)), 'data'
   )
   app.config['FILEALCHEMY_MODELS'] = (Author,)

   FileAlchemy(app, db).load_data()

Flask-FileAlchemy then reads your data from the :code:`data/` directory, and
stores them in an in-memory data store (using the :code:`sqlite://:memory:`
engine provided by SQLAlchemy).

Please note that it's not possible to write to this database using
:code:`db.session`. Well, technically it's allowed, but the changes your app
makes will only be reflected in the in-memory data store but won't be persisted
to disk.

.. _Flask: http://flask.pocoo.org
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _Frozen-Flask: https://pythonhosted.org/Frozen-Flask/
.. _SQLAlchemy: https://flask-admin.readthedocs.io/en/latest/
