from os import environ, path
from db import entities
from datetime import datetime
import utils


from cerberus.validator import Validator
import sqlalchemy
from sqlalchemy.orm import sessionmaker


engine = sqlalchemy.create_engine(
    'postgresql+psycopg2://{}:{}@{}/{}'.format(
      environ.get('POSTGRES_USER'),
      environ.get('POSTGRES_PASSWORD'),
      "db",
      environ.get('POSTGRES_DB')
    ),
    echo=True
  )
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
entities.Base.metadata.create_all(engine)
entities.Command.metadata.create_all(engine)
entities.Document.metadata.create_all(engine)
entities.DocumentAtom.metadata.create_all(engine)
session.commit()


def new_session(device_info):
  """
  Generates a new session given uniquely identifying device info
  :param device_info:object
  :return: (Error, token:string)
  """
  entities.Base.metadata.create_all(engine)
  entities.Command.metadata.create_all(engine)
  entities.Document.metadata.create_all(engine)
  entities.DocumentAtom.metadata.create_all(engine)
  session.commit()

  if not isinstance(device_info, dict):
    return TypeError("device_info must be a dict"), ""

  device_info["cpu_count"] = int(device_info.get("cpu_count"))

  validator = Validator({
    'os': {
      'type': 'string'
    },
    'cpu_count': {
      'type': 'integer'
    },
    'release': {
      'type': 'string'
    },
    'hostname': {
      'type': 'string'
    }
  })

  if not validator.validate(device_info):
    return TypeError("Invalid device_info input was given"), ""

  session_entity = entities.Session(
    os=device_info.get("os"),
    cpu_count=device_info.get("cpu_count"),
    release=device_info.get("release"),
    hostname=device_info.get("hostname")
  )
  session.add_all([session_entity])
  session.commit()
  return None, session_entity.id


def command_execute(uttered, session_id):
  """
  Parse out a command and execute command as wanted
  :param uttered:string
  :param session_id:int
  :return: (Error, dict)
  """
  commands = [
    "go to", "go to full", "go to link",
    "search",
    "login Facebook", "logout Facebook",
    "read messages", "read timeline",
    "read notifications"
  ]
  commands_standardized = {
    "go to": "goto",
    "go to full": "goto_full",
    "go to link": "goto_link",
    "login Facebook": "facebook_login",
    "logout Facebook": "facebook_logout",
    "search": "search",
    "read messages": "facebook_messages",
    "read timeline": "facebook_timeline",
    "read notifications": "facebook_notifications"
  }

  actual, utterance_substring = utils.determine_command(
    uttered, commands
  )
  if actual is None or utterance_substring is None:
    return ValueError("Command doesn't exist"), {}

  actual_command_standardized = commands_standardized.get(actual)
  command_entity = entities.Command(
    session_id=session_id,
    command=actual_command_standardized
  )
  session.add_all([command_entity])
  session.commit()

  '''
  If command transcription from text/speech requires
  no further processing, we are done!
  '''
  if actual_command_standardized in [
    "facebook_login",
    "facebook_logout",
    "facebook_messages",
    "facebook_timeline",
    "facebook_notifications"
  ]:
    return None, {
      "utterance": uttered,
      "command": actual_command_standardized
    }

  '''
  Command transcriptions that require further processing
  '''
  _, command_utterance_parameter = uttered.split(utterance_substring, 1)
  if not command_utterance_parameter:
    return ValueError("Command parameter not provided"), {}

  normalized_parameter = utils.nlp_tools.text_to_link(
    command_utterance_parameter
  )

  '''
  If we have cached results from prior goto executions,
  use those cached results instead to save time!
  '''
  if actual_command_standardized == "goto":
    documents = session\
      .query(entities.Document)\
      .filter(entities.Document.website.like("%"+normalized_parameter+"%"))\
      .all()

    if len(documents) > 0:
      return map(
        lambda document_atom: {
          "doc_id": document_atom.document_id,
          "rank": document_atom.rank,
          "type": document_atom.type,
          "text": document_atom.text,
          "entity": document_atom.entity
        },
        [document.document_atoms for document in documents]
      )

  results = []
  if actual_command_standardized == "goto":
    results = utils.info_cards(normalized_parameter)
  elif actual_command_standardized == "goto_full":
    results = utils.info_cards(normalized_parameter, full=True)
  elif actual_command_standardized == "goto_link":
    results = utils.info_cards(normalized_parameter)
  elif actual_command_standardized == "search":
    results = utils.search(normalized_parameter)

  '''
  Never executed a goto operation on this link before?
  Save our results now!
  '''
  if actual_command_standardized == "goto":
    new_document = entities.Document(
      website=normalized_parameter
    )
    session.add_all(new_document)
    session.commit()
    session.add_all(
      [entities.DocumentAtom(
        rank=result.rank,
        text=result.text,
        type=result.type,
        entity=result.entity,
        document_id=new_document.id
      ) for result in results]
    )
  session.commit()

  return None, {
    "utterance": uttered,
    "command": actual_command_standardized,
    "cards": results
  }


def command_audio(audio_file, session_id):
  """
  Transcribe an audio file command into its text form and process accordingly
  :param audio_file:string
  :param session_id:int
  :return: (Error, dict)
  """
  if not isinstance(audio_file, basestring):
    return TypeError("audio_file must be a string"), ""

  if not path.exists(audio_file):
    return IOError("audio_file does not exist"), ""

  transcription = utils.audio_transcribe(audio_file)
  if transcription is None:
    return TypeError("No sensible audio was picked up"), ""

  return command_execute(transcription, session_id)
