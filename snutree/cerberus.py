
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

def describe_schema(schema, **indent_args):
    '''
    Returns a string containing the descriptions of all the fields in the
    schema document, in a YAML-like format.
    '''
    indent_args.setdefault('tabstop', 2)
    lines = __describe_schema(Indent(**indent_args), schema)
    return '\n'.join(lines)

def __describe_schema(indent, schema):

    for key, rules in schema.items():

        description = rules.get('description')
        schema_type = rules.get('type')

        if schema_type == 'dict':
            subschema = rules.get('schema', {})
            valueschema = rules.get('valueschema', {})
            keyschema = rules.get('keyschema', {})
            yield from __describe_dict_schema(indent, key, description, subschema, keyschema, valueschema)
        elif schema_type == 'list':
            listschema = rules.get('schema')
            yield from __describe_list_schema(indent, key, description, listschema)
        else:
            default = str(rules['default']) if 'default' in rules else None
            yield from __describe_scalar_schema(indent, key, default, description)

def __describe_dict_schema(indent, key, description, subschema, keyschema, valueschema):

    KEY = keyschema.get('description', 'KEY')
    schema = dict(subschema, **({
        f'<{KEY}1>' : valueschema,
        f'<{KEY}2>' : {'default' : '...'}
        } if valueschema else {}))

    yield from __describe_scalar_schema(indent, key, None, description)
    with indent.indented():
        yield from __describe_schema(indent, schema)

def __describe_list_schema(indent, key, description, listschema):

    item_description = listschema.get('description', 'ITEM')

    yield from __describe_scalar_schema(indent, key, None, description)
    with indent.indented():
        yield from __describe_row(indent, '-', None, f'{item_description}1')
        with indent.indented():
            yield from __describe_schema(indent, listschema.get('schema', {}))
        yield from __describe_row(indent, '-', '...', None)

def __describe_scalar_schema(indent, key, default, description):
    yield from __describe_row(indent, f'{key}:', default, description)

def __describe_row(indent, prefix, value, comment):
    row = []
    row.append(f'{indent}{prefix}')
    if value is not None:
        row.append(value)
    if comment is not None:
        row.append(f'# {comment}')
    yield ' '.join(row)

