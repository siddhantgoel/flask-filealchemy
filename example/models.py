from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'

    slug = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)


class Book(Base):
    __tablename__ = 'books'

    slug = Column(String(255), primary_key=True)
    title = Column(String(255), nullable=False)
    author_slug = Column(String(255), ForeignKey('authors.slug'),
                         nullable=False)
    bestseller = Column(Boolean, server_default='false')
