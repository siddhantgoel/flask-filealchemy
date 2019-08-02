Flask-FileAlchemy
=================

.. image:: https://badge.fury.io/py/flask-filealchemy.svg
    :target: https://pypi.python.org/pypi/flask-filealchemy

.. image:: https://travis-ci.org/siddhantgoel/flask-filealchemy.svg?branch=stable
    :target: https://travis-ci.org/siddhantgoel/flask-filealchemy

:code:`Flask-FileAlchemy` lets you use YAML-formatted plain-text files as the
data store for your Flask_ app.

Installation
------------

.. code-block:: bash

   $ pip install flask-filealchemy

Background
----------

While there are better data stores to use in production than plain-text, the
constraints on data stores for applications that only have to run locally are
much more relaxed. For such applications, it's normally OK to sacrifice on
performance for ease of use.

One very strong use case here is generating static sites. While you can use
`Frozen-Flask`_ to "freeze" an entire Flask application to a set of HTML files,
your application still needs to read data from somewhere. This means you'll need
to set up a data store, which (locally) tends to be file based SQLite. While
that does the job extremely well, this also means executing SQL statements to
input data.

Depending on how many data models you have and what types they contain, this
can quickly get out of hand (imagine having to write an :code:`INSERT` statement
for a blog post).

In addition, you can't version control your data. Well, technically you can,
but the diffs won't make any sense to a human.

Flask-FileAlchemy lets you use an alternative data store - plain text files.

Plain text files have the advantage of being much easier to handle for a human.
Plus, you can version control them so your application data and code are both
checked in together and share history.

Flask-FileAlchemy lets you enter your data in YAML formatted plain text files
and loads them according to the SQLAlchemy_ models you've defined using
`Flask-SQLAlchemy`_ This data is then put into whatever data store you're using
(in-memory SQLite works best) and is then ready for your app to query however it
pleases.

This lets you retain the comfort of dynamic sites without compromising on the
simplicity of static sites.

Usage
-----

Define your data models using the standard (Flask-)SQLAlchemy API.

.. code-block:: python

   app = Flask(__name__)

   # configure Flask-SQLAlchemy
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

   db = SQLAlchemy(app)

   class BlogPost(db.Model):
       __tablename__ = 'blog_posts'

       slug = Column(String(255), primary_key=True)
       title = Column(String(255), nullable=False)
       contents = Column(Text, nullable=False)

Then, create a :code:`data/` directory somewhere on your disk (to keep things
simple, it's recommended to have this directory in the application root). For
each model you've defined, create a directory under this :code:`data/` directory
with the same name as the :code:`__tablename__` attribute.

In this example, we'll add the following contents to
:code:`data/blog_posts/first-post-ever.yml`.

.. code-block:: yaml

   slug: first-post-ever
   title: First post ever!
   contents: |
      This blog post talks about how it's the first post ever!

For "smaller" models which don't have more than 2-3 fields, Flask-FileAlchemy
supports reading from an :code:`_all.yml` file. In such a case, instead of
adding one file for every row, simply add all the rows in the :code:`_all.yml`
file inside the table directory.

In this example, this could look like the following.

.. code-block:: yaml

   - slug: first-post-ever
     title: First post ever!
     contents: This blog post talks about how it's the first post ever!
   - slug: second-post-ever
     title: second post ever!
     contents: This blog post talks about how it's the second post ever!

Finally, configure :code:`Flask-FileAlchemy` with your setup and ask it to load
all your data.

.. code-block:: python

   # configure Flask-FileAlchemy
   app.config['FILEALCHEMY_DATA_DIR'] = os.path.join(
       os.path.dirname(os.path.realpath(__file__)), 'data'
   )
   app.config['FILEALCHEMY_MODELS'] = (BlogPost,)

   # load tables
   FileAlchemy(app, db).load_tables()

:code:`Flask-FileAlchemy` then reads your data from the given directory, and
stores them in the data store of your choice that you configured
:code:`Flask-FileAlchemy` with (the preference being
:code:`sqlite:///:memory:`).

Please note that it's not possible to write to this database using
:code:`db.session`. Well, technically it's allowed, but the changes your app
makes will only be reflected in the in-memory data store but won't be persisted
to disk.

Contributing
------------

Contributions are most welcome!

Please make sure you have Python 3.5+ and Poetry_ installed.

1. Git clone the repository -
   :code:`git clone https://github.com/siddhantgoel/flask-filealchemy`.

2. Install the packages required for development -
   :code:`poetry install`.

3. That's basically it. You should now be able to run the test suite -
   :code:`poetry run py.test`.

.. _Flask: http://flask.pocoo.org
.. _Flask-SQLAlchemy: http://flask-sqlalchemy.pocoo.org/
.. _Frozen-Flask: https://pythonhosted.org/Frozen-Flask/
.. _Poetry: https://poetry.eustace.io/
.. _SQLAlchemy: https://www.sqlalchemy.org/
