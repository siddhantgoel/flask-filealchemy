from pathlib import Path

import frontmatter
from sqlalchemy.schema import Table

from .common import parse_yaml_file


class InvalidLoaderError(Exception):
    pass


class BaseLoader:
    """
    Base class for all Loader classes.
    """

    def __init__(self, data_dir: Path, table: Table):
        self.data_dir = data_dir
        self.table = table

        self.validate()

    def extract_records(self, model):
        raise NotImplementedError()

    def validate(self):
        raise NotImplementedError()


class YAMLFileLoader(BaseLoader):
    """
    YAMLFileLoader is used to load records from directories which contain
    a `_all.yml` file.

    Please note that while the existence of this file is a necessary
    requirement, this loader would still be chosen if the directory contains
    other files.
    """

    @property
    def data_path(self):
        return self.data_dir.joinpath(self.table.name).joinpath('_all.yml')

    def extract_records(self, model):
        values = parse_yaml_file(self.data_path.as_posix())

        for value in values:
            kwargs = {
                column.name: value.get(column.name)
                for column in self.table.columns
            }

            yield model(**kwargs)

    def validate(self):
        all_ = self.data_path

        if not all_.exists() or not all_.is_file():
            raise InvalidLoaderError()


class _DirectoryLoaderValidateMixin:
    def validate(self):
        for file_ in self.data_path.iterdir():
            if not any(
                ext for ext in self.extensions if file_.name.endswith(ext)
            ):
                raise InvalidLoaderError()


class YAMLDirectoryLoader(_DirectoryLoaderValidateMixin, BaseLoader):
    """
    YAMLDirectoryLoader is used to load records from directories which contain
    only YAML-formatted files.
    """

    extensions = ('.yml', '.yaml', '.YML', '.YAML')

    @property
    def data_path(self):
        return self.data_dir.joinpath(self.table.name)

    def extract_records(self, model):
        for entry in self.data_path.iterdir():
            if not entry.is_file():
                continue

            values = parse_yaml_file(
                self.data_dir.joinpath(self.table.name)
                .joinpath(entry.name)
                .as_posix()
            )

            kwargs = {
                column.name: values.get(column.name)
                for column in self.table.columns
            }

            yield model(**kwargs)


class MarkdownFrontmatterDirectoryLoader(
    _DirectoryLoaderValidateMixin, BaseLoader
):
    """
    MarkdownFrontmatterDirectoryLoader is used to load records from directories
    which contain only markdown/front-matter formatted files.
    """

    extensions = ('.md', '.MD', '.markdown')
    content_column_name = 'content'

    @property
    def data_path(self):
        return self.data_dir.joinpath(self.table.name)

    def extract_records(self, model):
        for entry in self.data_path.iterdir():
            if not entry.is_file():
                continue

            values = frontmatter.load(
                self.data_dir.joinpath(self.table.name)
                .joinpath(entry.name)
                .as_posix()
            )

            kwargs = {
                column.name: values.get(column.name)
                for column in self.table.columns
                if column.name != self.content_column_name
            }
            kwargs[self.content_column_name] = values.content

            yield model(**kwargs)


def loader_for(data_dir: Path, table: Table):
    for cls in (
        MarkdownFrontmatterDirectoryLoader,
        YAMLFileLoader,
        YAMLDirectoryLoader,
    ):
        try:
            loader = cls(data_dir, table)
        except InvalidLoaderError:
            pass
        else:
            return loader
