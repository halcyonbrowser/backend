from os import environ
import enum
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext import declarative

sqlalchemy.create_engine(
  'postgresql+psycopg2://{}:{}@/{}'.format(
    environ.get('POSTGRES_USER'),
    environ.get('POSTGRES_PASSWORD'),
    environ.get('POSTGRES_DB')
  ),
  echo=True
)
Base = declarative.declarative_base()


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


class Command(Base):
  __tablename__ = 'command'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
  session_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey('session.id'))
  '''
  command is either
    "goto --website--", "goto_full --website--"
    "search", "login_facebook"
  '''
  command = sqlalchemy.Column(sqlalchemy.TEXT)
  time = sqlalchemy.Column(sqlalchemy.TIMESTAMP)

  session = sqlalchemy.orm.relationship(
    'Session',
    back_populates='commands'
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


class DocumentAtom(Base):

  class TypeEnum(enum.Enum):
    highlight = "highlight"
    image_description = "image_description"
    factoid = "factoid"
    link = "link"

  class EntityEnum(enum.Enum):
    person = "person"
    organization = "organization"
    location = "location"
    money = "money"
    percent = "percent"
    date = "date"
    time = "time"

  __tablename__ = 'document_atom'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
  document_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey('document.id'))
  rank = sqlalchemy.Column(sqlalchemy.Integer)
  text = sqlalchemy.Column(sqlalchemy.TEXT)
  type = sqlalchemy.Column(sqlalchemy.Enum(TypeEnum))
  entity = sqlalchemy.Column(sqlalchemy.Enum(EntityEnum))

  document = sqlalchemy.orm.relationship(
    'Document',
    back_populates='document_atoms'
  )
