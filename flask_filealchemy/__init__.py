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
            warnings.warn('Flask-FileAlchemy: no models found')

    def load_data(self):
        self.db.create_all()

        try:
            session = self.db.session

            for model in self._models:
                path = os.path.join(self._data_dir, model.__name__)

                if not os.path.isdir(path):
                    continue

                for file_ in os.listdir(path):
                    data = None

                    try:
                        with open(os.path.join(path, file_)) as fd:
                            data = fd.read()
                    except IOError:
                        warnings.warn('Unable to read {}'.format(file_))
                        continue

                    values = load(data)

                    session.add(model(**values))
        except Exception:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()
