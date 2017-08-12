from voluptuous import Schema, Required, Coerce
from voluptuous.humanize import validate_with_humanized_errors
from voluptuous.error import Error
from snutree.tree import Member
from snutree.utilities.voluptuous import NonEmptyString, SnutreeValidationError
from snutree.utilities import Semester

RankType = Semester

def dicts_to_members(dicts, **conf):
    '''
    Validate a table of keyed member dictionaries.
    '''
    try:
        for dct in dicts:
            yield KeyedMember.from_dict(dct)
    except Error as exc:
        raise SnutreeValidationError(exc, dct)

schema_information = {
        'key' : "Member ID",
        'name' : "Member name",
        'big_key' : "ID of member's big",
        'pledge_semester' : 'Semester the member joined (e.g., "Fall 2000" or "Spring 1999")',
        }

class KeyedMember(Member):
    '''
    A Member keyed by some ID.
    '''

    schema = Schema({
            Required('key') : NonEmptyString,
            Required('name') : NonEmptyString,
            'big_key' : NonEmptyString,
            Required('pledge_semester') : Coerce(RankType),
            })

    def __init__(self,
            key=None,
            name=None,
            pledge_semester=None,
            big_key=None
            ):

        self.key = key
        self.name = name
        self.rank = pledge_semester
        self.parent = big_key

    @classmethod
    def validate_dict(cls, dct):
        return validate_with_humanized_errors(dct, cls.schema)

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate_dict(dct))

    def get_dot_label(self):
        return self.name

