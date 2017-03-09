import pprint
from .. import SnutreeError
from . import Semester

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

def validate(validator, dct):
    '''
    Validate the dict with the cerberus validator provided. Return the
    validated dict on success and provided error information on failure.
    '''

    dct = validator.validated(dct)
    if not dct:
        errors = pprint.pformat(validator.errors)
        s = 's' if len(errors) != 1 else ''
        msg = f'Error{s} found in configuration:\n{errors}'
        raise SnutreeError(msg)

    return dct

