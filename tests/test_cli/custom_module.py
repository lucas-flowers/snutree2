from voluptuous import Schema, Required, Coerce
from snutree.utilities.voluptuous import NonEmptyString
from snutree.tree import Member

def dicts_to_members(dicts):
    for d in dicts:
        yield SubMember.from_dict(d)

schema_information = {
        'cid' : 'Member ID',
        'pid' : 'Parent ID',
        's' : 'Rank ID',
        }

class SubMember(Member):

    validate = Schema({
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
        self.rank = s
        self.parent = pid

    def get_dot_label(self):
        return self.key

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate(dct))

