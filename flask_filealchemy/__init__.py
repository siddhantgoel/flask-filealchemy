import os
import warnings

from yaml import load


class FileAlchemy:
    _log_prefix = 'flask-filealchemy'

    def __init__(self, app, db):
        self.app = app
        self.db = db

        self._data_dir = self.app.config.get('FILEALCHEMY_DATA_DIR')
        self._models = self.app.config.get('FILEALCHEMY_MODELS')
        self._logger = self.app.logger

        if not self._models:
            warnings.warn('{}: no models found'.format(self._log_prefix))

    def load_tables(self):
        self.db.create_all()

        for table in self.db.metadata.sorted_tables:
            self._load_table(table)

    def _load_table(self, table):
        path = os.path.join(self._data_dir, table.name)

        try:
            session = self.db.session

            for file_name in os.listdir(path):
                obj = self._load_row(table, file_name)

                if not obj:
                    self._logger.warn('{}: unable to read {}'.format(
                        self._log_prefix, file_name))
                    continue

                session.add(obj)
                self._logger.info(
                    '{}: imported {}'.format(self._log_prefix, file_name))

            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _load_row(self, table, file_name):
        data = None

        try:
            path = os.path.join(self._data_dir, table.name, file_name)

            with open(path) as fd:
                data = fd.read()
        except IOError:
            return None

        values = None

        try:
            values = load(data)
        except ValueError:
            return None

        kwargs = {
            column.name: values.get(column.name)
            for column in table.columns
        }

        model_cls = self._model_for(table)

        return model_cls(**kwargs)

    def _model_for(self, table):
        for model_cls in self._models:
            if model_cls.__tablename__ == table.name:
                return model_cls
