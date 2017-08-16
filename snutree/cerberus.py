
'''
Additional functions for cerberus-style validation.
'''

import pprint
import cerberus
from .errors import SnutreeError

class Validator(cerberus.Validator):

    def validated(self, dct):
        '''
        Validate the dict with the cerberus validator provided. Return the
        validated dict on success and provided error information on failure.
        '''

        dct = super().validated(dct)
        if not dct:
            errors = pprint.pformat(self.errors)
            s = 's' if len(errors) != 1 else ''
            msg = f'Error{s} found in configuration:\n{errors}'
            raise SnutreeError(msg)

        return dct

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

