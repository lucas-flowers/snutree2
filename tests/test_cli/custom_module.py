from voluptuous import Schema, Required, Coerce
from snutree.entity import Member
from snutree.utilities.voluptuous import NonEmptyString

def validate(rows):
    for row in rows:
        yield SubMember.from_dict(row)

class SubMember(Member):

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

    def get_dot_label(self):
        return self.key

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validator(dct))

