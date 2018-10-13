import os
from collections import Mapping

from sqlalchemy.exc import IntegrityError
from yaml import load


class LoadError(Exception):
    pass


def _fmt_log(message):
    return 'flask-filealchemy: {}'.format(message)


class FileAlchemy:
    def __init__(self, app, db):
        self.app = app
        self.db = db

        self._data_dir = self.app.config.get('FILEALCHEMY_DATA_DIR')
        self._models = self.app.config.get('FILEALCHEMY_MODELS')
        self._logger = self.app.logger

        if not self._models:
            self._logger.warn(_fmt_log('no models found'))

    def load_tables(self):
        if not os.path.isdir(self._data_dir):
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
        path = os.path.join(self._data_dir, table.name)

        for file_name in os.listdir(path):
            obj = self._load_row(table, file_name)

            session.add(obj)

            self._logger.info(_fmt_log('imported {}'.format(file_name)))

        try:
            session.flush()
        except IntegrityError as e:
            raise LoadError(e)

    def _load_row(self, table, file_name):
        data = None

        try:
            path = os.path.join(self._data_dir, table.name, file_name)

            with open(path) as fd:
                data = fd.read()
        except IOError:
            raise LoadError(_fmt_log('could not open {}'.format(file_name)))

        values = None

        try:
            values = load(data)

            if not isinstance(values, Mapping):
                raise ValueError()
        except ValueError:
            raise LoadError(_fmt_log('{} has invalid data'.format(file_name)))

        kwargs = {
            column.name: values.get(column.name)
            for column in table.columns
        }

        model_cls = self._model_for(table)

        if not model_cls:
            raise LoadError(
                _fmt_log('{} model not available'.format(table.name)))

        return model_cls(**kwargs)

    def _model_for(self, table):
        for model_cls in self._models:
            if model_cls.__tablename__ == table.name:
                return model_cls
