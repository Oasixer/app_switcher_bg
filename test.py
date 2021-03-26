import re
TERMITE_MATCH_REGEX = re.compile('(^nvim)|(sudo -E nvim)|(sudo nvim)')

def is_nvim(window_title):
    return TERMITE_MATCH_REGEX.match(window_title)
