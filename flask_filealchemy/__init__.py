import os
import warnings

from yaml import load


class FileAlchemy:
    def __init__(self, app, db):
        self.app = app
        self.db = db

        self._data_dir = self.app.config.get('FILEALCHEMY_DATA_DIR')
        self._models = self.app.config.get('FILEALCHEMY_MODELS')

        if not self._models:
            warnings.warn('flask-filealchemy: no models found')

    def load_data(self):
        self.db.create_all()

        for table in self.db.metadata.sorted_tables:
            path = os.path.join(self._data_dir, table.name)

            if not os.path.isdir(path):
                continue

            try:
                session = self.db.session

                for file_ in os.listdir(path):
                    data = None

                    try:
                        with open(os.path.join(path, file_)) as fd:
                            data = fd.read()
                    except IOError:
                        warnings.warn(
                            'flask-filealchemy: unable to read {}'.format(
                                file_))
                        continue

                    values = load(data)

                    kwargs = {
                        column.name: values.get(column.name)
                        for column in table.columns
                    }

                    model = self._model_for(table.name)

                    session.add(model(**kwargs))
            except Exception:
                session.rollback()
                raise
            else:
                session.commit()
            finally:
                session.close()

    def _model_for(self, table_name):
        for model in self._models:
            if model.__tablename__ == table_name:
                return model
