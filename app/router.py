from os import environ, path
import time
from flask import Flask, request, json


app = Flask(__name__)
AUDIO_COMMAND_TEMP = environ.get('AUDIO_COMMAND_TEMP')


@app.route('/')
def default():
  app.logger.debug('GET /')
  return 'Welcome to Halcyon Backend REST-ful API'


@app.route('/init', methods=['POST'])
def init():
  app.logger.debug('POST /init')
  token = request.get_json(force=True, silent=True)


@app.route('/command_audio', methods=['POST'])
def command_audio():
  app.logger.debug('POST /command_audio')

  file_name = AUDIO_COMMAND_TEMP + str(int(time.time()))
  file_obj = request.files['command']
  file_obj.save(file_name)
