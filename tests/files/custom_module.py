from voluptuous import Schema, Required, Coerce
from snutree.voluptuous import NonEmptyString
from snutree.tree import Member

Rank = int

def to_Members(dicts, **conf):
    for d in dicts:
        yield SubMember.from_dict(d)

description = {
        'cid' : 'Member ID',
        'pid' : 'Parent ID',
        's' : 'Rank ID',
        }

class SubMember(Member):

    validate = Schema({
        Required('cid') : NonEmptyString,
        'pid' : NonEmptyString,
        Required('s') : Coerce(Rank)
        })

    def __init__(self,
            cid=None,
            pid=None,
            s=None,
            ):

        self.key = cid
        self.rank = s
        self.parent = pid

    @property
    def label(self):
        return self.key

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate(dct))

