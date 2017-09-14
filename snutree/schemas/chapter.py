from voluptuous import Schema, Required, Coerce
from voluptuous.error import Error
from voluptuous.humanize import validate_with_humanized_errors
from snutree.errors import SnutreeSchemaError
from snutree.tree import Member
from snutree.utilities.voluptuous import NonEmptyString

Rank = int

def to_Members(dicts, **config):
    '''
    Validate a table of chapters dictionaries.
    '''
    try:
        for dct in dicts:
            yield Chapter.from_dict(dct)
    except Error as exc:
        raise SnutreeSchemaError(exc, dct)

description = {
        'child' : 'Chapter name',
        'parent' : "Name of the chapter's parent chapter",
        'founded' : 'Year the chapter was founded',
        }

class Chapter(Member):
    '''
    A chapter, key by its name.
    '''

    schema = Schema({
        'parent' : NonEmptyString,
        Required('child') : NonEmptyString,
        Required('founded') : Coerce(Rank)
        })

    def __init__(self,
            parent=None,
            child=None,
            founded=None,
            ):

        self.key = child
        self.rank = founded
        self.parent = parent

    @property
    def label(self):
        return self.key

    @classmethod
    def validate_dict(cls, dct):
        return validate_with_humanized_errors(dct, cls.schema)

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate_dict(dct))

