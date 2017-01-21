from os import environ, path
from db import entities
import itertools
import utils

import fuzzy
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
session = (sessionmaker().configure(bind=engine))()


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


def command_execute(uttered):
  """
  Parse out a command and execute command as wanted
  :return: (Error, dict)
  """
  commands = [
    "go to", "go to full",
    "search", "login Facebook",
    "read messages", "read timeline",
    "read notifications", "logout Facebook"
  ]

  def determine_command(uttered, commands):
    """
    Determine the command that was uttered
    :param uttered: phrase given by user
    :return: (command, uttered substring)
    """
    words = uttered.split()
    words_powerset = [
      " ".join(combination)
      for r in range(1, len(words))
      for combination in itertools.combinations(words, r)
    ]

    d_metaphone = fuzzy.DMetaphone()
    commands_dmetaphone = [
      (command, d_metaphone(command))
      for command in commands
      ]
    words_powerset_dmetaphone = [
      (combination, d_metaphone(combination))
      for combination in words_powerset
    ]

    for (command, command_dmeta) in commands_dmetaphone:
      for (uttered, uttered_dmeta) in words_powerset_dmetaphone:
        if len(set(command_dmeta).intersection(set(uttered_dmeta))):
          return command, uttered

    return None, None

  actual, utterance_substring = determine_command(uttered, commands)
  if actual is None or utterance_substring is None:
    return ValueError("Command doesn't exist"), {}


def command_audio(audio_file):
  """
  Transcribe an audio file command into its text form and process accordingly
  :param audio_file:
  :return: (Error, dict)
  """
  if not isinstance(audio_file, dict):
    return TypeError("audio_file must be a string"), ""

  if not path.exists(audio_file):
    return IOError("audio_file does not exist"), ""

  transcription = utils.audio_transcribe(audio_file)
  if transcription is None:
    return TypeError("No audio was picked up"), ""

  return command_execute(transcription)

