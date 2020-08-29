from pathlib import Path
import pytest

from sqlalchemy import Column, String

from flask_filealchemy.loaders import (
    BaseLoader,
    loader_for,
    YAMLDirectoryLoader,
    YAMLFileLoader,
)


def test_base_loader_does_not_validate():
    with pytest.raises(NotImplementedError):
        BaseLoader(None, None)


def test_model_for_single_file(db, tmpdir):
    authors = tmpdir.mkdir('authors')
    authors.join('_all.yml').write('does-not-matter')

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    assert len(db.metadata.sorted_tables) == 1
    assert db.metadata.sorted_tables[0].name == 'authors'

    author_table = db.metadata.sorted_tables[0]

    assert isinstance(
        loader_for(Path(tmpdir.strpath), author_table), YAMLFileLoader
    )


def test_model_for_directory_extra_files(db, tmpdir):
    authors = tmpdir.mkdir('authors')

    authors.join('invalid.md').write('does-not-matter')
    authors.join('valid.yml').write('does-not-matter')

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    assert len(db.metadata.sorted_tables) == 1
    assert db.metadata.sorted_tables[0].name == 'authors'

    author_table = db.metadata.sorted_tables[0]

    assert not loader_for(Path(tmpdir.strpath), author_table)


def test_model_for_directory_normal(db, tmpdir):
    authors = tmpdir.mkdir('authors')

    authors.join('first.yml').write('does-not-matter')
    authors.join('second.yml').write('does-not-matter')

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    assert len(db.metadata.sorted_tables) == 1
    assert db.metadata.sorted_tables[0].name == 'authors'

    author_table = db.metadata.sorted_tables[0]

    assert isinstance(
        loader_for(Path(tmpdir.strpath), author_table), YAMLDirectoryLoader
    )


def test_model_for_directory_extra_extensions(db, tmpdir):
    authors = tmpdir.mkdir('authors')

    for index, extension in enumerate(YAMLDirectoryLoader.extensions):
        authors.join('authors-{}.{}'.format(index, extension)).write(
            'does-not-matter'
        )

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    assert len(db.metadata.sorted_tables) == 1
    assert db.metadata.sorted_tables[0].name == 'authors'

    author_table = db.metadata.sorted_tables[0]

    assert isinstance(
        loader_for(Path(tmpdir.strpath), author_table), YAMLDirectoryLoader
    )
