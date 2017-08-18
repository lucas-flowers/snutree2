
'''
Additional functions for cerberus-style validation.
'''

import pprint
import cerberus
from pathlib import Path
from .errors import SnutreeError

class Validator(cerberus.Validator):

    def __init__(self, *args, **kwargs):
        self.RankType = kwargs.get('RankType')
        super().__init__(*args, **kwargs)

    def validated(self, *args, **kwargs):
        '''
        Validate the dict with the cerberus validator provided. Return the
        validated dict on success and provided error information on failure.
        '''

        dct = super().validated(*args, **kwargs)
        if not dct:
            errors = pprint.pformat(self.errors)
            s = 's' if len(errors) != 1 else ''
            msg = f'Error{s} found in configuration:\n{errors}'
            raise SnutreeError(msg)

        return dct

    def _normalize_coerce_optional_path(self, value):
        return value and Path(value)

    def _normalize_coerce_rank_type(self, value):
        if not self.RankType:
            raise ValueError('cannot coerce rank value: validator RankType field not defined')
        return self.RankType(value)

    def _normalize_coerce_optional_rank_type(self, value):
        return value and self._normalize_coerce_rank_type(value)

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

