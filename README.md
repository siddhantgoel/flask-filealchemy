# flask-filealchemy

For small applications that don't need to run in production, the constraints on
the database you choose are much more relaxed. Often SQLite just works fine. In
fact, it's the recommended data store because data stores like PostgreSQL are
overkill for this purpose.

While SQLite works perfectly, you still need to insert data into it somehow.
[Flask Admin] does that job quite nicely, but it's still another layer on top of
your database.

This package proposes an alternative solution - text files.

The idea is to use plain text files as your data store. You define your data
models (based on what [SQLAlchemy] allows) and then add your data in a `data/`
directory.

`flask-filealchemy` then reads your data models, converts them into SQLAlchemy
classes on the fly, reads your data from the `data/` directory, stores them in
an in-memory data store (using the `sqlite://:memory:` engine provided by
SQLAlchemy), and then gives you a handle which you can use to query that data.

Please note, that this handle is "read-only". While writing using this handle is
technically allowed, the changes your app makes will only be reflected in the
in-memory data store but won't be persisted to disk.

[Flask-Admin]: https://flask-admin.readthedocs.io/en/latest/
[SQLAlchemy]: https://www.sqlalchemy.org/
