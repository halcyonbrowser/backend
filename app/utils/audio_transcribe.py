import speech_recognition

recognizer = speech_recognition.Recognizer()


def audio_transcribe(file_path):
  """
  Transcribe an audio file into string text
  @param {string} file_path - absolute file path
  @returns {string|null} transcribed text
  """

  try:
    with speech_recognition.AudioFile(file_path) as source:
      audio = recognizer.record(source)
  except ValueError:
    return None
  
  try:
    transcribed_text = recognizer.recognize_sphinx(audio)
    return transcribed_text
  except speech_recognition.UnknownValueError:
    return None
  except speech_recognition.RequestError:
    return None
