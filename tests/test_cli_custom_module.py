from voluptuous import In, Schema, Optional, Coerce
from snutree.directory import Directory
from snutree.entity import Initiate
from snutree.utilities import NonEmptyString

def directory(members):
    return Directory(members, [SubInitiate])

class SubInitiate(Initiate):

    allowed = {'I'}
    validator = Schema({
        'status' : In('I'),
        'cid' : NonEmptyString,
        Optional('pid') : NonEmptyString,
        's' : Coerce(int)
        })

    def __init__(self,
            status=None,
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

