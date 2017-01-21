from enum import Enum
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext import declarative


Base = declarative.declarative_base()


class Command(Base):
  __tablename__ = 'command'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
  session_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey('session.id'))
  command = sqlalchemy.Column(sqlalchemy.TEXT)
  time = sqlalchemy.Column(sqlalchemy.TIMESTAMP)

  session = sqlalchemy.orm.relationship(
    'Session',
    back_populates='commands'
  )


class Session(Base):
  __tablename__ = 'session'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
  time = sqlalchemy.Column(sqlalchemy.TIMESTAMP)
  os = sqlalchemy.Column(sqlalchemy.VARCHAR)
  cpu_count = sqlalchemy.Column(sqlalchemy.Integer)
  release = sqlalchemy.Column(sqlalchemy.VARCHAR)
  hostname = sqlalchemy.Column(sqlalchemy.VARCHAR)

  commands = sqlalchemy.orm.relationship(
    'Command',
    back_populates='session',
    order_by=Command.time
  )


class DocumentAtom(Base):

  __tablename__ = 'document_atom'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
  document_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('document.id'))
  rank = sqlalchemy.Column(sqlalchemy.Integer)
  text = sqlalchemy.Column(sqlalchemy.TEXT)
  type = sqlalchemy.Column(sqlalchemy.Enum(
    Enum("highlight", "media", "factoid", "link")
  ))
  entity = sqlalchemy.Column(sqlalchemy.Enum(
    Enum("person", "organization", "location",
         "money", "percent", "date", "time"))
  )

  document = sqlalchemy.orm.relationship(
    'Document',
    back_populates='document_atoms'
  )


class Document(Base):
  __tablename__ = 'document'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
  website = sqlalchemy.Column(sqlalchemy.String)

  document_atoms = sqlalchemy.orm.relationship(
    'DocumentAtom',
    back_populates='document',
    order_by=DocumentAtom.rank
  )
