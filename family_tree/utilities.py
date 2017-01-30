import logging
from family_tree.semester import Semester

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

def logged(function):
    def wrapped(*args, **kwargs):
        logging.info('Started %s . . .', function.__name__)
        result = function(*args, **kwargs)
        logging.info('Finished!')
        return result
    return wrapped

