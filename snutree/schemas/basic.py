from voluptuous import Schema, Required, Coerce
from snutree.entity import Member
from snutree.directory import Directory
from snutree.semester import Semester
from snutree.utilities import NonEmptyString

def directory(members):
    return Directory(members, [KeylessMember])

class KeylessMember(Member):

    allowed = {'Initiate'}

    validator = Schema({
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

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return self.key

