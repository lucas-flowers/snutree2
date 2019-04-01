
from itertools import dropwhile

from jsonschema import Draft7Validator, FormatChecker

# Graph identifiers, which are also classes (which require special handling)
GRAPHS = [
    'root',
    'tree',
    'rank',
]

# Fields that are templates, also requiring special handling
TEMPLATE_ATTRIBUTES = [
    'label',
]

def validate(config):

    format_checker = FormatChecker()
    format_checker.checks('classMap', raises=ValueError)(class_map)

    validator = Draft7Validator(
        schema=schema,
        format_checker=format_checker,
    )

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

    'type': 'object',
    'additionalProperties': False,

    'properties': {

        'class': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {

                # Graph attributes for the root graph, rank subgraphs, and tree subgraph
                'graph': {
                    'type': 'object',
                    'format': 'classMap',
                    'propertyNames': {'enum': GRAPHS},
                    'additionalProperties': {'$ref': '#/definitions/attributes'},
                },

                # Node attributes for difference classes
                'node': {
                    'type': 'object',
                    'format': 'classMap',
                    'propertyNames': {'$ref': '#/definitions/id'},
                    'additionalProperties': {'$ref': '#/definitions/attributes'},
                },

                # Edge attributes for different classes
                'edge': {
                    'type': 'object',
                    'format': 'classMap',
                    'propertyNames': {'$ref': '#/definitions/id'},
                    'additionalProperties': {'$ref': '#/definitions/attributes'},
                },

            },
        },

        'custom': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {

                # Custom nodes
                'node': {
                    'type': 'object',
                    'propertyNames': {'$ref': '#/definitions/id'},
                    'additionalProperties': {'$ref': '#/definitions/attributes'},
                },

                # Custom edges
                'edge': {
                    'type': 'object',
                    'propertyNames': {'$ref': '#/definitions/edgeId'},
                    'additionalProperties': {'$ref': '#/definitions/attributes'},
                },

            },
        },

    },

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

        # DOT attributes
        'attributes': {
            'type': 'object',
            'additionalProperties': {
                'type': [
                    'string',
                    'number',
                ],
            },
        },

    },

}

