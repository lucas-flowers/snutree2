from voluptuous import Schema, Required, Coerce
from voluptuous.humanize import validate_with_humanized_errors
from snutree.entity import Member, validate_members
from snutree.semester import Semester
from snutree.utilities import NonEmptyString

def validate(members):
    return validate_members(members, [KeylessMember])

class KeylessMember(Member):

    allowed = {'Initiate'}

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
    def from_dict(cls, dct):
        return cls(**validate_with_humanized_errors(dct, cls.schema))

    def get_dot_label(self):
        return self.key

