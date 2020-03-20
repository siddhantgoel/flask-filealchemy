from pathlib import Path
import pytest

from sqlalchemy import Column, String

from flask_filealchemy.loaders import (
    BaseLoader,
    loader_for,
    YAMLSingleFileLoader,
    YAMLDirectoryLoader,
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
        loader_for(Path(tmpdir.strpath), author_table), YAMLSingleFileLoader
    )


def test_model_for_directory(db, tmpdir):
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
