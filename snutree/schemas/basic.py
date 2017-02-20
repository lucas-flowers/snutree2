from voluptuous import Schema, In, Optional, Coerce
from ..directory import Directory
from ..entity import Initiate
from ..semester import Semester
from ..utilities import NonEmptyString

class KeylessInitiate(Initiate):

    allowed = {'Initiate'}

    validator = Schema({
            'status' : In(allowed),
            'name' : NonEmptyString,
            Optional('big_name') : NonEmptyString,
            'pledge_semester' : Coerce(Semester),
            })

    def __init__(self,
            status=None,
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

class DefaultDirectory(Directory):
    member_types = [KeylessInitiate]
    ignored_statuses = []

