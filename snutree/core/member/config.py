
from dataclasses import dataclass
from typing import Optional, Tuple, List, Mapping

from jsonschema import Draft7Validator

from ...utilities import deep_update
from .parser import Parser

def validate(config):
    Draft7Validator(schema).validate(config)

# The very lenient JSON schema (lenient for the user)
schema = {

    'definitions': {

        'string': {
            'type': ['string', 'null'],
        },

        'list': {
            'anyOf': [
                {'type': 'null'},
                {'type': 'array', 'items': {'$ref': '#/definitions/string'}},
            ],
        },

        'map': {
            'anyOf': [
                {'type': 'null'},
                {'type': 'object', 'additionalProperties': {'$ref': '#/definitions/string'}},
            ],
        },

    },

    'type': 'object',
    'additionalProperties': False,

    'properties': {

        'id': {'$ref': '#/definitions/string'},
        'parent_id': {'$ref': '#/definitions/string'},
        'rank': {'$ref': '#/definitions/string'},
        'classes': {'$ref': '#/definitions/list'},
        'data': {'$ref': '#/definitions/map'},

        'custom': {
            'anyOf': [
                {'type': 'null'},
                {'type': 'array', 'items': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'id': {'$ref': '#/definitions/string'},
                        'parent_id': {'$ref': '#/definitions/string'},
                        'rank': {'$ref': '#/definitions/string'},
                        'classes': {'$ref': '#/definitions/list'},
                        'data': {'$ref': '#/definitions/map'},
                    },
                }},
            ],
        },

    },

}

defaults = {
    'classes': ['root', 'tree', 'member'],
}

@dataclass
class Config:

    Function = Tuple[str, List[str]]

    id: Optional[str]
    parent_id: Optional[str]
    rank: Optional[str]
    classes: List[Function]
    data: Mapping[str, Function]
    custom: List[dict]

    @classmethod
    def from_dict(cls, dct, defaults=True, validate=True):
        '''
        Assumes nothing (or very, very little) about the configuration, but
        gives the program view into the configuration that it expects without
        too much guessing.
        '''

        if defaults:
            dct = deep_update(globals()['defaults'], dct)

        if validate:
            globals()['validate'](dct)

        parser = Parser()
        return cls(
            id=(
                parser.parse(dct['id'])
                if dct.get('id') else None
            ),
            parent_id=(
                parser.parse(dct['parent_id'])
                if dct.get('parent_id') else None
            ),
            rank=(
                parser.parse(dct['rank'])
                if dct.get('rank') else None
            ),
            classes=[
                parser.parse(string)
                for string in (dct.get('classes') or [])
            ],
            data={
                destination: parser.parse(string)
                for destination, string in (dct.get('data') or {}).items()
            },
            custom=[
                {
                    'id': member.get('id') or None,
                    'parent_id': member.get('parent_id') or None,
                    'rank': member.get('rank') or None,
                    'classes': member.get('classes') or [],
                    'data': member.get('data') or {}
                } for member in (
                    custom or {}
                    for custom in (dct.get('custom') or [])
                )
            ],
        )

