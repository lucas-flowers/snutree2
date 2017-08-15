
'''
Additional functions for voluptuous-style validation.
'''

import re

DIGITS_MATCHER = re.compile(r'\d+')

def Digits(s):
    '''
    Matches a string that consists only of digits. Throws a ValueError on
    failure to match.
    '''
    match = DIGITS_MATCHER.match(s)
    if match:
        return match.group(0)
    raise ValueError

def NonEmptyString(s):
    '''
    Matches a nonempty string and throws a ValueError otherwise.
    '''
    if isinstance(s, str) and len(s) > 0:
        return s
    raise ValueError

