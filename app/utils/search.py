from os import environ

from googleapiclient.discovery import build


def search(search_term):
  """
  Search Google for the uttered search term
  :param search_term:string - search term
  :return: SearchResultsList schema
  """
  def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

  results = google_search(
    search_term,
    environ.get("GOOGLE_API_KEY", ""),
    environ.get("GOOGLE_CSE_ID", ""),
  )

  def mapper(result):
    """
    nlp.annotate(result.title, properties = {
      'annotators': 'ner',
      'outputFormat': 'json'
    })
    """

    return {
      "doc_id": result.cacheId,
      "title": result.title,
      "text": result.snippet,
      "type": "search result",
      "entity": "organization"
    }

  return map(mapper, results[:20])
