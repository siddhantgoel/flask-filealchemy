from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class MissingModelsError(Exception):
    pass


class FileAlchemy:
    def __init__(self, app):
        self.app = app

        self._engine = create_engine('sqlite:///:memory:')
        self._sessionmaker = sessionmaker(bind=self._engine)

        self._models = self.app.config.get('FILEALCHEMY_MODELS')

        if not self._models:
            raise MissingModelsError()

        self._load_data()

    def _load_data(self):
        pass

    @contextmanager
    def session(self):
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
