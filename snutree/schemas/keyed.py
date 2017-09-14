from voluptuous import Schema, Required, Coerce
from voluptuous.error import Error
from voluptuous.humanize import validate_with_humanized_errors
from snutree.errors import SnutreeSchemaError
from snutree.tree import Member
from snutree.utilities.voluptuous import NonEmptyString
from snutree.utilities.semester import Semester

Rank = Semester

def to_Members(dicts, **config):
    '''
    Validate a table of keyed member dictionaries.
    '''
    try:
        for dct in dicts:
            yield KeyedMember.from_dict(dct)
    except Error as exc:
        raise SnutreeSchemaError(exc, dct)

description = {
        'key' : "Member ID",
        'name' : "Member name",
        'big_key' : "ID of member's big",
        'semester' : 'Semester the member joined (e.g., "Fall 2000" or "Spring 1999")',
        }

class KeyedMember(Member):
    '''
    A Member keyed by some ID.
    '''

    schema = Schema({
            Required('key') : NonEmptyString,
            Required('name') : NonEmptyString,
            'big_key' : NonEmptyString,
            Required('semester') : Coerce(Rank),
            })

    def __init__(self,
            key=None,
            name=None,
            semester=None,
            big_key=None
            ):

        self.key = key
        self.name = name
        self.rank = semester
        self.parent = big_key

    @classmethod
    def validate_dict(cls, dct):
        return validate_with_humanized_errors(dct, cls.schema)

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate_dict(dct))

    @property
    def label(self):
        return self.name

