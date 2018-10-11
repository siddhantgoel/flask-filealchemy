import os
import warnings
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from yaml import load

DeclarativeBase = declarative_base()


class MissingModelsError(Exception):
    pass


class FileAlchemy:
    def __init__(self, app):
        self.app = app

        self._engine = create_engine('sqlite:///:memory:')
        self._sessionmaker = sessionmaker(bind=self._engine)

        self._data_dir = self.app.config.get('FILEALCHEMY_DATA_DIR')
        self._models = self.app.config.get('FILEALCHEMY_MODELS')

        if not self._models:
            raise MissingModelsError()

        self._load_data()

    def _load_data(self):
        DeclarativeBase.metadata.create_all(self._engine)

        with self.make_session() as session:
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
            session.commit()

    @contextmanager
    def make_session(self):
        try:
            session = self._sessionmaker()
            yield session
        except Exception:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()
