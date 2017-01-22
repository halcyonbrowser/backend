from os import environ, path
import time
from flask import Flask, request, json

import actions


app = Flask(__name__)
AUDIO_COMMAND_TEMP = environ.get('AUDIO_COMMAND_TEMP')


@app.route('/')
def default():
  app.logger.debug('GET /')
  return 'Welcome to Halcyon Backend REST-ful API!'


@app.route('/init', methods=['POST'])
def init():
  app.logger.debug('POST /init')
  payload = request.get_json(force=True, silent=True)
  device_info = payload.get("devid")

  error, token = actions.new_session(device_info)

  if isinstance(error, BaseException):
    response = json.jsonify({
      "status": 400,
      "error": error.message
    })
    response.status_code = 400
  else:
    response = json.jsonify({
      "status": 200,
      "token": token
    })
    response.status_code = 200

  return response


@app.route('/command_audio', methods=['POST'])
def command_audio():
  app.logger.debug('POST /command_audio')
  payload = request.get_json(force=True, silent=True)
  session_id = payload.get("token")

  file_name = path.join(AUDIO_COMMAND_TEMP, str(int(time.time() * 1000)))
  file_obj = request.files['command']
  file_obj.save(file_name)

  error, results = actions.command_audio(file_name, session_id)

  if isinstance(error, BaseException):
    response = json.jsonify({
      "status": 400,
      "error": error.message
    })
    response.status_code = 400
  else:
    response = json.jsonify({
      "status": 200,
      "results": results
    })
    response.status_code = 200

  return response
