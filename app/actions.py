from os import environ, path
from db import entities
from datetime import datetime
import utils


from cerberus.validator import Validator
import sqlalchemy
from sqlalchemy.orm import sessionmaker


engine = sqlalchemy.create_engine(
    'postgresql+psycopg2://{}:{}@/{}'.format(
      environ.get('POSTGRES_USER'),
      environ.get('POSTGRES_PASSWORD'),
      environ.get('POSTGRES_DB')
    ),
    echo=True
  )
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


def new_session(device_info):
  """
  Generates a new session given uniquely identifying device info
  :param device_info:object
  :return: (Error, token:string)
  """
  if not isinstance(device_info, dict):
    return TypeError("device_info must be a dict"), ""

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
    os=device_info.os,
    cpu_count=device_info.cpu_count,
    release=device_info.release,
    hostname=device_info.hostname
  )
  session.add_all(session_entity)
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
    command=actual_command_standardized,
    time=datetime.now().microsecond
  )
  session.add_all(command_entity)
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
  _, command_utterance_parameter = uttered.split(utterance_substring)
  if not command_utterance_parameter:
    return ValueError("Command parameter not provided"), {}

  if actual_command_standardized == "goto":
    utils.info_cards(command_utterance_parameter)
  elif actual_command_standardized == "goto_full":
    utils.info_cards(command_utterance_parameter, full=True)
  elif actual_command_standardized == "goto_link":
    utils.info_cards(command_utterance_parameter)
  elif actual_command_standardized == "search":
    utils.search(command_utterance_parameter)

  return None, {
    "utterance": uttered,
    "command": actual_command_standardized
  }


def command_audio(audio_file, session_id):
  """
  Transcribe an audio file command into its text form and process accordingly
  :param audio_file:string
  :param session_id:int
  :return: (Error, dict)
  """
  if not isinstance(audio_file, dict):
    return TypeError("audio_file must be a string"), ""

  if not path.exists(audio_file):
    return IOError("audio_file does not exist"), ""

  transcription = utils.audio_transcribe(audio_file)
  if transcription is None:
    return TypeError("No sensible audio was picked up"), ""

  return command_execute(transcription, session_id)
