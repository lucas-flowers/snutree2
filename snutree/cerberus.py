
'''
Additional functions for cerberus-style validation.
'''

import pprint
from pathlib import Path
import cerberus
from .errors import SnutreeError
from .indent import Indent

class Validator(cerberus.Validator):

    def __init__(self, schema, *args, **kwargs):
        self.RankType = kwargs.get('RankType')
        super().__init__(schema, *args, **kwargs)

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

    def _validate_description(self, description, field, value):
        ''' { 'type' : 'string', 'nullable' : False } '''
        pass

    def _normalize_coerce_optional_path(self, value):
        return value and Path(value)

    def _normalize_coerce_rank_type(self, value):
        if not self.RankType:
            raise ValueError('cannot coerce rank value: validator RankType field not defined')
        return self.RankType(value)

    def _normalize_coerce_optional_rank_type(self, value):
        return value and self._normalize_coerce_rank_type(value)

def description_schema(schema, descriptions=None):
    '''
    Return a dictionary of 'description' fields from the provided
    Cerberus-style schema. Each element in the return dictionary has a schema
    field containing the descriptions of its subkeys, and a description field
    for itself.
    '''
    descriptions = descriptions if descriptions is not None else {}
    for key, rules in schema.items():
        description = rules.get('description', '')
        default = rules.get('default')
        if default is not None:
            description = ' '.join([description, f'(default: {default!r})'])
        descriptions[key] = {'description' : description}
        if rules.get('type') == 'dict' and 'schema' in rules:
            descriptions[key]['schema'] = description_schema(rules['schema'], {})
    return descriptions

def describe_schema(schema):
    '''
    Returns a string containing the descriptions of all the fields in the
    schema document, formatted similarly to (but not the same as) YAML.
    '''
    descriptions = description_schema(schema)
    lines = __describe_schema(descriptions, Indent(tabstop=2))
    return '\n'.join(lines)

def __describe_schema(descriptions, indent):
    for key, dct in descriptions.items():
        description = dct['description']
        schema = dct.get('schema')
        yield f'{indent}{key}: {description}'
        if schema:
            with indent.indented():
                yield from __describe_schema(schema, indent)

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

