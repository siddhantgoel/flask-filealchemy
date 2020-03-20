from pathlib import Path

from sqlalchemy.schema import Table

from .common import parse_yaml_file


class InvalidLoaderError(Exception):
    pass


class BaseLoader:
    def __init__(self, data_dir: Path, table: Table):
        self.data_dir = data_dir
        self.table = table

        self.validate()

    def extract_records(self, model):
        raise NotImplementedError()

    def validate(self):
        raise NotImplementedError()


class YAMLSingleFileLoader(BaseLoader):
    @property
    def data_path(self):
        return self.data_dir.joinpath(self.table.name).joinpath('_all.yml')

    def extract_records(self, model):
        values = parse_yaml_file(self.data_path)

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


class YAMLDirectoryLoader(BaseLoader):
    @property
    def data_path(self):
        return self.data_dir.joinpath(self.table.name)

    def extract_records(self, model):
        for entry in self.data_path.iterdir():
            if not entry.is_file():
                continue

            values = parse_yaml_file(
                self.data_dir.joinpath(self.table.name).joinpath(entry.name)
            )

            kwargs = {
                column.name: values.get(column.name)
                for column in self.table.columns
            }

            yield model(**kwargs)

    def validate(self):
        for file_ in self.data_path.iterdir():
            if not file_.name.endswith('.yml'):
                raise InvalidLoaderError()


def loader_for(data_dir: Path, table: Table):
    for cls in (YAMLSingleFileLoader, YAMLDirectoryLoader):
        try:
            loader = cls(data_dir, table)
        except InvalidLoaderError:
            pass
        else:
            return loader
