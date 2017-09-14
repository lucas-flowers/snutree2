from itertools import product
from voluptuous import Schema, Required, Coerce
from snutree.utilities.voluptuous import NonEmptyString
from snutree.tree import Member

def to_Members(dicts, **conf):
    Class.initialize_names(conf['start_year'], conf['last_year'] + 1)
    yield from (SubMember.from_dict(dct) for dct in dicts)

description = {
        'key' : 'Member ID',
        'name' : 'Member name',
        'big_key' : 'Big ID',
        'year' : 'Year',
        }

class Class(int):

    def __add__(self, other):
        return Class(super(Class, self).__add__(other))

    def __sub__(self, other):
        return Class(super(Class, self).__sub__(other))

    def __str__(self):
        if self - self.start_year in range(0, len(self.class_names)):
            class_name = ''.join(self.class_names[self - self.start_year])
            return '{year}: {ID}'.format(year=int(self), ID=class_name)
        else:
            return str(int(self))

    @classmethod
    def initialize_names(cls, start_year, stop_year):
        cls.start_year = start_year
        cls.stop_year = stop_year
        cls.class_names = list(
            name for _, name in
            zip(range(start_year, stop_year), class_name_generator())
        )

LETTERS = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ'
def class_name_generator():
    repeat = 1
    while True:
        yield from (''.join(p) for p in product((LETTERS), repeat=repeat))
        repeat += 1

Rank = Class

class SubMember(Member):

    validate = Schema({
        Required('key') : NonEmptyString,
        Required('name') : NonEmptyString,
        'big_key' : NonEmptyString,
        Required('year') : Coerce(Rank)
        })

    def __init__(self,
            key=None,
            name=None,
            big_key=None,
            year=None,
            ):

        self.name = name
        self.key = key
        self.rank = year
        self.parent = big_key

    @property
    def label(self):
        return self.name

    @classmethod
    def from_dict(cls, dct):
        return cls(**cls.validate(dct))

