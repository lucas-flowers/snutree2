from voluptuous import Schema, Required, Coerce
from voluptuous.humanize import validate_with_humanized_errors
from voluptuous.error import Error
from snutree.tree import Member
from snutree.utilities.voluptuous import NonEmptyString, SnutreeValidationError

def dicts_to_members(dicts):
    '''
    Validate a table of chapters dictionaries.
    '''
    try:
        for d in dicts:
            yield Chapter.from_dict(d)
    except Error as e:
        raise SnutreeValidationError(e, d)

class Chapter(Member):
    '''
    A chapter, key by its name.
    '''

    schema = Schema({
        'mother' : NonEmptyString,
        Required('child') : NonEmptyString,
        Required('founded') : Coerce(int)
        })

    def __init__(self,
            mother=None,
            child=None,
            founded=None,
            ):

        self.key = child
        self.rank = founded
        self.parent = mother

    def get_dot_label(self):
        return self.key

    @classmethod
    def validate_dict(cls, dct):
        return validate_with_humanized_errors(dct, cls.schema)

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate_dict(dct))

