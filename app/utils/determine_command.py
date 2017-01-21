import itertools
import fuzzy


def determine_command(uttered, commands):
  """
  Determine the command that was uttered
  :param uttered: phrase given by user
  :return: (command, uttered substring)
  """

  '''
  Absolute 100% match between a command and utterance
  '''
  if uttered in commands:
    return uttered, uttered

  '''
    A command is a substring of utterance
  '''
  words = uttered.split()
  words_powerset = [
    " ".join(combination)
    for r in range(1, len(words))
    for combination in itertools.combinations(words, r)
  ]

  def best_match(best_match_sofar, current_match):
    if len(current_match) > len(best_match_sofar):
      return current_match

    return best_match_sofar

  plain_matching = reduce(
    best_match,
    set(words_powerset).intersection(commands),
    ""
  )
  if plain_matching:
    return plain_matching, plain_matching

  '''
  Fuzzy phonetic match when all else fails
  '''
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
