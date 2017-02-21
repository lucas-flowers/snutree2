from voluptuous import Schema, In, Coerce
from ..entity import Initiate
from ..directory import Directory
from ..utilities import NonEmptyString

def directory(members):
    return Directory(members, [Chapter])

class Chapter(Initiate):

    allowed = {'Chapter'}

    validator = Schema({
        'status' : In(allowed),
        'mother' : NonEmptyString,
        'child' : NonEmptyString,
        'founded' : Coerce(int)
        })

    def __init__(self,
            mother=None,
            child=None,
            founded=None,
            **ignore
            ):

        self.key = child
        self.semester = founded
        self.parent = mother

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return self.key

