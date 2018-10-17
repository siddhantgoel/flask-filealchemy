from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml
from sqlalchemy.exc import IntegrityError


class LoadError(Exception):
    pass


def _fmt_log(message):
    return 'flask-filealchemy: {}'.format(message)


def _parse_yaml_file(file_):
    try:
        with file_.open() as fd:
            data = fd.read()

        values = yaml.load(data)

        if isinstance(values, Sequence):
            for value in values:
                if not isinstance(value, Mapping):
                    raise ValueError()
        elif not isinstance(values, Mapping):
            raise ValueError()
    except IOError:
        raise LoadError(_fmt_log('could not open {}'.format(file_)))
    except ValueError:
        raise LoadError(_fmt_log('{} contains invalid YAML'.format(file_)))
    else:
        return values


class FileAlchemy:
    def __init__(self, app, db):
        self.app = app
        self.db = db

        self._data_dir = Path(self.app.config.get('FILEALCHEMY_DATA_DIR'))
        self._models = self.app.config.get('FILEALCHEMY_MODELS')
        self._logger = self.app.logger

        if not self._models:
            self._logger.warn(_fmt_log('no models found'))

    def load_tables(self):
        if not self._data_dir.exists():
            raise LoadError(
                _fmt_log('{} is not a directory'.format(self._data_dir)))

        self.db.create_all()

        try:
            session = self.db.session

            for table in self.db.metadata.sorted_tables:
                self._load_table(session, table)
        except LoadError:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()

    def _load_table(self, session, table):
        records = self._extract_records(table)

        for record in records:
            session.add(record)

        try:
            session.flush()
        except IntegrityError as e:
            raise LoadError(e)

    def _extract_records(self, table):
        all_ = self._data_dir.joinpath(table.name).joinpath('_all.yml')

        if all_.is_file():
            records = self._load_table_from_all(table)
        else:
            records = self._load_table_from_files(table)

        return records

    def _load_table_from_all(self, table):
        values = _parse_yaml_file(
            self._data_dir.joinpath(table.name).joinpath('_all.yml')
        )

        return [
            self._record_from_mapping(table, value)
            for value in values
        ]

    def _record_from_mapping(self, table, values):
        kwargs = {
            column.name: values.get(column.name)
            for column in table.columns
        }

        model_cls = self._model_for(table)

        if not model_cls:
            raise LoadError(
                _fmt_log('{} model not available'.format(table.name)))

        return model_cls(**kwargs)

    def _load_table_from_files(self, table):
        path = self._data_dir.joinpath(table.name)

        return [
            self._load_row_from_file(table, file_.name)
            for file_ in path.iterdir()
            if not file_.is_dir()
        ]

    def _load_row_from_file(self, table, file_name):
        values = _parse_yaml_file(
            self._data_dir.joinpath(table.name).joinpath(file_name)
        )

        return self._record_from_mapping(table, values)

    def _model_for(self, table):
        for model_cls in self._models:
            if model_cls.__tablename__ == table.name:
                return model_cls
