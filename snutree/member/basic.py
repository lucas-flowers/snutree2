from voluptuous import Schema, Required, Coerce
from voluptuous.humanize import validate_with_humanized_errors
from voluptuous.error import Error
from snutree.utilities.voluptuous import NonEmptyString
from snutree.utilities import Semester
from snutree.tree import Member
from snutree import SnutreeError

def dicts_to_members(dicts):
    '''
    Convert member dictionaries to member objects.
    '''
    try:
        for d in dicts:
            yield KeylessMember.from_dict(d)
    except Error:
        raise SnutreeError('Error in {}'.format(d))

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
        self.semester = pledge_semester
        self.parent = big_name

    @classmethod
    def validate_dict(cls, dct):
        return validate_with_humanized_errors(dct, cls.schema)

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate_dict(dct))

    def get_dot_label(self):
        return self.key

