from voluptuous import Schema, Required, Coerce
from snutree.entity import Member, validate_members
from snutree.utilities import NonEmptyString

def validate(members):
    return validate_members(members, [SubMember])

class SubMember(Member):

    allowed = {'I'}
    validator = Schema({
        Required('cid') : NonEmptyString,
        'pid' : NonEmptyString,
        Required('s') : Coerce(int)
        })

    def __init__(self,
            cid=None,
            pid=None,
            s=None,
            ):

        self.key = cid
        self.semester = s
        self.parent = pid

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return self.key

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validator(dct))

