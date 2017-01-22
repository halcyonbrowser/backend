import nlp_tools


def info_cards(link, full=False):
  """
  Generate cards of information based on the site that is being processed
  :param link:string - website to obtain information from
  :return: SearchResultsList schema
  """

  content = nlp_tools.link_to_content(link)

  if full:
    return content

  return nlp_tools.content_to_results(content)
