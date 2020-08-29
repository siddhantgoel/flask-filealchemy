from textwrap import dedent

import pytest
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from flask_filealchemy import FileAlchemy, LoadError


def test_directory_does_not_exist(db):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    db.app.config['FILEALCHEMY_MODELS'] = (Author,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = '/does/not/exist/'

    with pytest.raises(LoadError):
        FileAlchemy(app, db).load_tables()


def test_invalid_directory(db, tmpdir):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    file_ = tmpdir.join('file.yml')
    file_.write('does not matter')

    db.app.config['FILEALCHEMY_MODELS'] = (Author,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = file_.strpath

    with pytest.raises(LoadError):
        FileAlchemy(app, db).load_tables()


def test_model_not_found(db, tmpdir):
    app = db.get_app()

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(32), primary_key=True)

    class Book(db.Model):
        __tablename__ = 'books'

        slug = Column(String(32), primary_key=True)

    data_dir = tmpdir.mkdir('data_dir')

    authors_dir = data_dir.mkdir('authors')
    max_mustermann = authors_dir.join('max-mustermann.yml')
    max_mustermann.write('slug: max-mustermann')

    books_dir = data_dir.mkdir('books')
    muster_book = books_dir.join('muster-book.yml')
    muster_book.write('slug: muster-book')

    db.app.config['FILEALCHEMY_MODELS'] = (Author,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir.strpath

    with pytest.raises(LoadError, match='no model found'):
        FileAlchemy(app, db).load_tables()


def test_load_yaml_single_table(db, tmpdir):
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
    db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir.strpath

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
        db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir.strpath

        with pytest.raises(LoadError):
            FileAlchemy(app, db).load_tables()


def test_yaml_foreign_keys(db, tmpdir):
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
    db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir.strpath

    FileAlchemy(app, db).load_tables()

    assert Author.query.count() == 1
    assert Book.query.count() == 2


def test_yaml_load_from_all_file(db, tmpdir):
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
    db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir.strpath

    FileAlchemy(app, db).load_tables()

    assert Author.query.count() == 2


def test_load_markdown(db, tmpdir):
    app = db.get_app()

    class Book(db.Model):
        __tablename__ = 'books'

        slug = Column(String(255), primary_key=True)
        title = Column(String(255), nullable=False)
        content = Column(Text, default=None)

    data_dir = tmpdir.mkdir('data_dir')

    authors_dir = data_dir.mkdir('books')
    first_book = authors_dir.join('first.md')
    second_book = authors_dir.join('second.md')

    first_book.write(
        dedent(
            '''
            ---
            slug: first
            title: First book
            ---

            This is the first book!
            '''
        )
    )

    second_book.write(
        dedent(
            '''
            ---
            slug: second
            title: Second book
            ---

            This is the second book!
            '''
        )
    )

    db.app.config['FILEALCHEMY_MODELS'] = (Book,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir.strpath

    FileAlchemy(app, db).load_tables()

    assert Book.query.count() == 2

    first = Book.query.filter_by(slug='first').one()
    assert first is not None
    assert first.content == 'This is the first book!'

    second = Book.query.filter_by(slug='second').one()
    assert second is not None
    assert second.content == 'This is the second book!'


def test_load_markdown_optional_fields(db, tmpdir):
    app = db.get_app()

    class Book(db.Model):
        __tablename__ = 'books'

        slug = Column(String(255), primary_key=True)
        title = Column(String(255), nullable=False)
        category = Column(String(255), default=None)
        content = Column(Text, default=None)

    data_dir = tmpdir.mkdir('data_dir')

    authors_dir = data_dir.mkdir('books')
    example = authors_dir.join('example.md')

    example.write(
        dedent(
            '''
            ---
            slug: example
            title: Example
            ---

            This is an example book.
            '''
        )
    )

    db.app.config['FILEALCHEMY_MODELS'] = (Book,)
    db.app.config['FILEALCHEMY_DATA_DIR'] = data_dir.strpath

    FileAlchemy(app, db).load_tables()

    assert Book.query.count() == 1

    book = Book.query.first()

    assert book is not None
    assert book.title == 'Example'
    assert book.slug == 'example'
    assert book.category is None
