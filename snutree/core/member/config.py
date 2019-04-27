
from jsonschema import Draft7Validator

def validate(config):
    Draft7Validator(schema).validate(config)

schema = {

    'type': 'object',
    'additionalProperties': False,
    # 'required': [
    #     'id',
    #     'parent_id',
    # ],

    'properties': {

        'id': {'type': 'string'},
        'parent_id': {'type': 'string'},
        'rank': {'type': 'string'},

        'classes': {
            'type': 'array',
            'items': {'type': 'string'},
        },

        'data': {
            'type': 'object',
            'additionalProperties': {'type': 'string'},
        },

    },

}

