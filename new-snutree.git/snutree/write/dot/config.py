
'''
Schema for DOT writer configuration.
'''

from dataclasses import dataclass
from itertools import dropwhile
from typing import Optional, List, Mapping, Union

from jsonschema import Draft7Validator, FormatChecker

from .create import Node, Edge
from ...utilities import get, deep_update

# Graph classes (which require special handling)
# TODO Move to dot.writer or figure out how to share it with dot.writer
GRAPHS = [
    'root',
    'tree',
    'rank',
]

def validate(config):
    format_checker = FormatChecker()
    format_checker.checks('classMap', raises=ValueError)(class_map)
    validator = Draft7Validator(schema, format_checker=format_checker)
    validator.validate(config)

def class_map(mapping):
    '''
    Later keys in a class map supersede earlier keys, in case of conflict.

    Because classes mapped to actual DOT subgraphs will always be overridden by
    custom classes, we force the subgraph classes to go first, to avoid
    confusion.
    '''

    remainder = mapping.keys()
    remainder = dropwhile('root'.__eq__, remainder)
    remainder = dropwhile({'rank', 'tree'}.__contains__, remainder)
    custom_classes = remainder

    if not set(GRAPHS).intersection(custom_classes):
        return True
    else:
        raise ValueError(
            'All custom classes must follow the "root", "rank", and'
            ' "tree" classes. The "root" class must come first.'
        )

schema = {

    'definitions': {

        # A subset of valid DOT identifiers
        'id': {
            'type': 'string',
            'pattern': '^([A-Za-z_][A-Za-z0-9_]*|[0-9]+)$',
        },

        # Two ids separated by a comma
        'edgeId': {
            'type': 'string',
            'pattern': '^([A-Za-z_][A-Za-z0-9_]*|[0-9]+),([A-Za-z_][A-Za-z0-9_]*|[0-9]+)$',
        },

        # Any other valid DOT value
        'value': {
            'anyOf': [
                {'type': 'number'},
                {'type': 'string'},
            ],
        },

        # DOT attributes
        'attributes': {'anyOf': [{'type': 'null'}, {
            'type': 'object',
            'propertyNames': {'$ref': '#/definitions/value'},
            'additionalProperties': {'$ref': '#/definitions/value'},
        }]},

        'classMap': {'anyOf': [{'type': 'null'}, {
            'type': 'object',
            'format': 'classMap',
            'propertyNames': {'$ref': '#/definitions/id'},
            'additionalProperties': {'$ref': '#/definitions/attributes'},
        }]},

    },

    'type': 'object',
    'additionalProperties': False,

    'required': [
        'names',
    ],

    'properties': {

        'seed': {
            'type': ['integer', 'null'],
        },

        'names': {
            'type': 'object',
            'additionalProperties': False,
            'required': [
                'root_graph_name',
                'tree_graph_name',
                'ranks_left_graph_name',
                'ranks_right_graph_name',
                'rank_key_suffix_left',
                'rank_key_suffix_right',
            ],
            'properties': {
                'root_graph_name': {'type': 'string'},
                'tree_graph_name': {'type': 'string'},
                'ranks_left_graph_name': {'type': 'string'},
                'ranks_right_graph_name': {'type': 'string'},
                'rank_key_suffix_left': {'type': 'string'},
                'rank_key_suffix_right': {'type': 'string'},
            },
        },

        'class': {
            'anyOf': [{'type': 'null'}, {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'graph': {'$ref': '#/definitions/classMap'},
                    'node': {'$ref': '#/definitions/classMap'},
                    'edge': {'$ref': '#/definitions/classMap'},
                },
            }],
        },

        'custom': {
            'anyOf': [{'type': 'null'}, {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'node': {'anyOf': [{'type': 'null'}, {
                        'type': 'object',
                        'propertyNames': {'$ref': '#/definitions/id'},
                        'additionalProperties': {'$ref': '#/definitions/attributes'},
                    }]},
                    'edge': {'anyOf': [{'type': 'null'}, {
                        'type': 'object',
                        'propertyNames': {'$ref': '#/definitions/edgeId'},
                        'additionalProperties': {'$ref': '#/definitions/attributes'},
                    }]},
                },
            }],
        },

    },

}

defaults = {
    'names': {
        'root_graph_name': 'root',
        'tree_graph_name': 'tree',
        'ranks_left_graph_name': 'ranksL',
        'ranks_right_graph_name': 'ranksR',
        'rank_key_suffix_left': 'L',
        'rank_key_suffix_right': 'R',
    }
}

@dataclass
class ClassConfig:

    AttributeMap = Mapping[Union[int, str], Union[int, str]]

    graph: AttributeMap
    node: AttributeMap
    edge: AttributeMap

    @classmethod
    def from_dict(cls, dct):
        return cls(
            graph=dct.get('graph') or {},
            node=dct.get('node') or {},
            edge=dct.get('edge') or {},
        )

@dataclass
class NameConfig:

    root_graph_name: str
    tree_graph_name: str
    ranks_left_graph_name: str
    ranks_right_graph_name: str
    rank_key_suffix_left: str
    rank_key_suffix_right: str

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(
            root_graph_name=dct['root_graph_name'],
            tree_graph_name=dct['tree_graph_name'],
            ranks_left_graph_name=dct['ranks_left_graph_name'],
            ranks_right_graph_name=dct['ranks_right_graph_name'],
            rank_key_suffix_left=dct['rank_key_suffix_left'],
            rank_key_suffix_right=dct['rank_key_suffix_right'],
        )

@dataclass
class Config:

    seed: Optional[int]
    names: NameConfig
    classes: ClassConfig
    edges: List[Edge]
    nodes: List[Node]

    @classmethod
    def from_dict(cls, dct, defaults=True, validate=True):

        if defaults:
            dct = deep_update(globals()['defaults'], dct)

        if validate:
            globals()['validate'](dct)

        return cls(
            seed=dct.get('seed'),
            names=NameConfig.from_dict(dct['names']),
            classes=ClassConfig.from_dict(dct.get('class') or {}),
            nodes=[
                Node(identifier, **attributes)
                for identifier, attributes in get(dct, 'custom', 'node').items()
            ],
            edges=[
                Edge(*identifiers.split(','), **attributes)
                for identifiers, attributes in get(dct, 'custom', 'edge').items()
            ],
        )

