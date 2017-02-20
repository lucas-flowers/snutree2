from voluptuous import Schema, In
from ..entity import Initiate
from ..directory import Directory
from ..utilities import NonEmptyString

class Chapter(Initiate):

    allowed = {'Chapter'}

    validator = Schema({
        'status' : In(allowed),
        'mother' : NonEmptyString,
        'child' : NonEmptyString,
        })

    def __init__(self,
            mother=None,
            child=None,
            **ignore
            ):

        self.key = child
        self.semester = None
        self.parent = mother

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return self.key

class ChapterDirectory(Directory):
    member_types = [Chapter]
    ignored_statuses = []

