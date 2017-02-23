import logging, time, pprint, re
from . import SnutreeError
from .semester import Semester

# TODO separate validation class?

DIGITS_MATCHER = re.compile('\d+')
def NonEmptyString(s):
    if isinstance(s, str) and len(s) > 0:
        return s
    raise ValueError
def Digits(s):
    match = DIGITS_MATCHER.match(s)
    if match:
        return match.group(0)
    raise ValueError 

# A required string; must be nonempty and not None
nonempty_string = {
        'type' : 'string',
        'required' : True,
        'empty' : False,
        'nullable' : False,
        }

# An optional string defaulting to None; must be nonempty if it does exist
optional_nonempty_string = {
        'type' : 'string',
        'default' : None,
        'empty' : False,
        'nullable' : True,
        }

# Optional boolean with True default
optional_boolean = {
        'type' : 'boolean',
        'default' : True,
        }

# Is a string coerceable to a semester
semester_like = {
        'coerce' : Semester
        }

# Optional version of semester_like that defaults to None
optional_semester_like = {
        'coerce' : lambda x : Semester(x) if x != None else None,
        }

def validate(validator, obj):

    obj = validator.validated(obj)
    if not obj:
        errors = validator.errors
        msg = 'Error{} found in options file:\n{}'
        vals = '' if len(errors) == 1 else 's', pprint.pformat(errors)
        raise SettingsError(msg.format(*vals))

    return obj

class SettingsError(SnutreeError):
    pass


def logged(function):

    logger = logging.getLogger(function.__module__)

    def wrapped(*args, **kwargs):
        logger.debug('%s started . . .', function.__name__)
        t0 = time.time()
        result = function(*args, **kwargs)
        logger.debug('%s finished in ~%.2f ms', function.__name__, (time.time() - t0) * 1000 )
        return result

    return wrapped

