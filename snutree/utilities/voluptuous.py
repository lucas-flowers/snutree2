import re
from .. import SnutreeError

DIGITS_MATCHER = re.compile('\d+')

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

class SnutreeValidationError(SnutreeError):
    '''
    Helper error for when using voluptuous to validate. When an error is caught
    in a specific row, send the error and the row to this error's constructor
    to raise a SnutreeError that will give a halfway-reasonable message.
    '''

    def __init__(self, voluptuous_error, data):
        self.err = voluptuous_error
        self.data = data

    def __str__(self):
        msg = '{}. In:\n{}'
        values = self.err, self.data
        return msg.format(*values)

