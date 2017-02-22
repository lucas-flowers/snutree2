from voluptuous import Schema, Coerce, Required
from snutree.entity import Member
from snutree.directory import Directory
from snutree.utilities import NonEmptyString

def directory(members):
    return Directory(members, [Chapter])

class Chapter(Member):

    allowed = {'Chapter'}

    validator = Schema({
        'mother' : NonEmptyString,
        Required('child') : NonEmptyString,
        Required('founded') : Coerce(int)
        })

    def __init__(self,
            mother=None,
            child=None,
            founded=None,
            ):

        self.key = child
        self.semester = founded
        self.parent = mother

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return self.key

