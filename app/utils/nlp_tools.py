from os import environ, path
import re
import time

import pdfkit
import slate


def text_to_link(uttered):
  """
  Converts text to HTTP links
  :param uttered:string
  :return: string
  """
  domain_endings = [
    "com",
    "org",
    "net",
    "edu",
    "gov",
    "mil"
  ]

  def tld_squash(accum, current_word):

    if len(accum) != 0:
      latest = accum.pop()

      if current_word in domain_endings and latest == "dot":
        accum.append("." + current_word)
        return accum
      else:
        accum.append(latest)

    accum.append(current_word)
    return accum

  return reduce(tld_squash, uttered.split(), [])


def link_to_content(link):
  """
  Given a link, obtain the core "content" of a web page
  :param link:
  :return:
  """
  pdf_path = path.join(environ.get("PDF_FILES_FOLDER"),
                       str(int(time.time() * 1000)))

  pdfkit.from_url(link, pdf_path, options={
    "no-images": False,
    "disable-javascript": False,
    "print-media-type": False
  })

  with open(pdf_path) as pdf_fp:
    link_contents = slate.PDF(pdf_fp)

  def clear_entities(text):
    ansi_escape = re.compile(r'\x1b[^m]*m')
    return ansi_escape.sub(' ', ' '.join(text.split()))

  corpus = ' '.join(
    map(clear_entities, link_contents)
  )
  return corpus


def content_to_results(corpus):
  """
  Corpus to results
  :param corpus:
  :return:
  """
  sentences = re.split(r' *[\.\?!][\'"\)\]]* *', corpus)
  print len(sentences)

  class TenTuple():
    count = 0

    def reducer(self, accum, sentence):
      if self.count == 10:
        self.count = 0
        accum.append(sentence)
        return accum

      if len(accum) == 0:
        self.count += 1
        accum.append(sentence)
        return accum

      latest = accum.pop()
      accum.append(latest + " " + sentence)
      self.count += 1
      return accum

  results = reduce(TenTuple().reducer, sentences, [])
  results_modified = []
  for index in range(0, len(results) - 1):
    results_modified.append({
      "text": results[index],
      "type": "summary",
      "entity": "page",
      "rank": index + 1
    })

  return results_modified
