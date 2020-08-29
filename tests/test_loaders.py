from pathlib import Path
import pytest

from sqlalchemy import Column, String

from flask_filealchemy.loaders import (
    BaseLoader,
    loader_for,
    MarkdownFrontmatterDirectoryLoader,
    YAMLDirectoryLoader,
    YAMLFileLoader,
)


def test_base_loader_does_not_validate():
    with pytest.raises(NotImplementedError):
        BaseLoader(None, None)


def test_yaml_file_loader(db, tmpdir):
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


def test_no_loader_found(db, tmpdir):
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


def test_yaml_directory_loader(db, tmpdir):
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


def test_yaml_directory_loader_with_extra_extensions(db, tmpdir):
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


def test_markdown_frontmatter_loader(db, tmpdir):
    authors = tmpdir.mkdir('authors')

    authors.join('first.md').write('does-not-matter')
    authors.join('second.md').write('does-not-matter')

    class Author(db.Model):
        __tablename__ = 'authors'

        slug = Column(String(255), primary_key=True)
        name = Column(String(255), nullable=False)

    assert len(db.metadata.sorted_tables) == 1
    assert db.metadata.sorted_tables[0].name == 'authors'

    author_table = db.metadata.sorted_tables[0]

    assert isinstance(
        loader_for(Path(tmpdir.strpath), author_table),
        MarkdownFrontmatterDirectoryLoader,
    )


def test_markdown_frontmatter_loader_with_extra_extensions(db, tmpdir):
    authors = tmpdir.mkdir('authors')

    for index, extension in enumerate(
        MarkdownFrontmatterDirectoryLoader.extensions
    ):
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
        loader_for(Path(tmpdir.strpath), author_table),
        MarkdownFrontmatterDirectoryLoader,
    )
