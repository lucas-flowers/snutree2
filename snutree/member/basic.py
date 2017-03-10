from voluptuous import Schema, Required, Coerce
from voluptuous.humanize import validate_with_humanized_errors
from voluptuous.error import Error
from snutree.tree import Member
from snutree.utilities.voluptuous import NonEmptyString, SnutreeValidationError
from snutree.utilities import Semester

def dicts_to_members(dicts):
    '''
    Convert member dictionaries to member objects.
    '''
    try:
        for dct in dicts:
            yield KeylessMember.from_dict(dct)
    except Error as exc:
        raise SnutreeValidationError(exc, dct)

def schema_information():
    '''
    Return a representation of the expected schema for this member type, for
    users.
    '''
    return {
            'name' : 'Member name',
            'big_name' : "Name of member's big",
            'pledge_semester' : 'Semester the member joined (e.g., "Fall 2000" or "Spring 1999")',
            }

class KeylessMember(Member):
    '''
    A Member keyed by their own name.
    '''

    schema = Schema({
        Required('name') : NonEmptyString,
        'big_name' : NonEmptyString,
        Required('pledge_semester') : Coerce(Semester),
        })

    def __init__(self,
            name=None,
            pledge_semester=None,
            big_name=None
            ):

        self.key = name
        self.rank = pledge_semester
        self.parent = big_name

    @classmethod
    def validate_dict(cls, dct):
        return validate_with_humanized_errors(dct, cls.schema)

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate_dict(dct))

    def get_dot_label(self):
        return self.key

