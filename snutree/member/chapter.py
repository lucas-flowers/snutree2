from voluptuous import Schema, Coerce, Required
from voluptuous.humanize import validate_with_humanized_errors
from snutree.entity import Member, validate_members
from snutree.utilities.voluptuous import NonEmptyString

def validate(chapters):
    '''
    Validate a list of chapters.
    '''
    return validate_members(chapters, Chapter)

class Chapter(Member):
    '''
    A chapter, key by its name.
    '''

    schema = Schema({
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

    def get_dot_label(self):
        return self.key

    @classmethod
    def from_dict(cls, dct):
        return cls(**validate_with_humanized_errors(dct, cls.schema))

