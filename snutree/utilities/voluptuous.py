import re

DIGITS_MATCHER = re.compile('\d+')

def Digits(s):
    match = DIGITS_MATCHER.match(s)
    if match:
        return match.group(0)
    raise ValueError

def NonEmptyString(s):
    if isinstance(s, str) and len(s) > 0:
        return s
    raise ValueError

