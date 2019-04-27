
'''
Create Member objects from lists of rows.
'''

from dataclasses import dataclass
from typing import Callable

from ...utilities import get, name
from ...utilities.semester import Semester
from .config import validate
from .parser import Parser
from .model import Member

def read(rows, config=None):
    return Reader(config or {}).read_members(rows)

def read_row(row, config=None):
    return Reader(config or {}).read_member(row)

class Functions:

    class FunctionNamespace(dict):
        def register(self, name):
            def wrapped(function):
                self[name] = function
                return staticmethod(function)
            return wrapped

    @dataclass
    class identified_by:
        identify: Callable[[object], str]
        def __call__(self, function):
            class Rank(function.__annotations__['return']):
                identify = self.identify
            return lambda *args, **kwargs: Rank(function(*args, **kwargs))

    rank = FunctionNamespace()

    @rank.register('Semester')
    @identified_by(lambda semester: f'{semester.season}{semester.year}'.lower())
    def semester(row, key) -> Semester:
        return row[key]

    @rank.register('Integer')
    @identified_by(str)
    def integer(row, key) -> int:
        return row[key]

    classes = FunctionNamespace()

    @classes.register(name=None)
    def constant(row, constant):
        return [constant]

    @classes.register('Enum')
    def enum(row, key):
        return [row[key]]

    @classes.register('Boolean')
    def boolean(row, key):
        value = row[key]
        if bool(value) and value.lower() in {'yes', 'true', '1'}:
            return [key]
        else:
            return []

    @classes.register('List')
    def list(row, key):
        value = row[key]
        return [
            element.strip() for element
            in (value.split(',') if value else [])
        ]

    data = FunctionNamespace()

    @data.register(name=None)
    def lookup(row, key):
        return row[key]

    @data.register('PreferredName')
    def preferred_name(row, first_key, preferred_key, last_key):
        return name.preferred(
            first_name=row[first_key],
            preferred_name=row[preferred_key],
            last_name=row[last_key],
        )

class Reader:

    parser = Parser()

    def __init__(self, config):
        self.config = config

    @property
    def config_id(self):
        return self.parser.parse(self.config['id'])

    @property
    def config_parent_id(self):
        return self.parser.parse(self.config['parent_id'])

    @property
    def config_rank(self):
        return self.parser.parse(self.config['rank'])

    @property
    def config_classes(self):
        return [
            self.parser.parse(string)
            for string in get(self.config, 'classes')
        ]

    @property
    def config_data(self):
        return {
            destination: self.parser.parse(string)
            for destination, string in get(self.config, 'data').items()
        }

    def read_members(self, rows):
        return [
            *map(self.read_member, rows),
            *map(self.read_custom_member, get(self.config, 'custom')),
        ]

    def read_member(self, row):
        return Member(
            id=self.read_id(row),
            parent_id=self.read_parent_id(row),
            rank=self.read_rank(row),
            classes=self.read_classes(row),
            data=self.read_data(row),
        )

    def read_custom_member(self, row):
        return Member(
            id=row.get('id'),
            parent_id=row.get('parent_id'),
            rank=(
                Functions.rank[self.config_rank[0]](row, 'rank')
                if self.config_rank is not None else None
            ),
            data=row.get('data') or {},
            classes=row.get('classes') or [],
        )

    def read_id(self, row):
        fname, keys = self.config_id
        return Functions.data[fname](row, *keys)

    def read_parent_id(self, row):
        fname, keys = self.config_parent_id
        return Functions.data[fname](row, *keys)

    def read_rank(self, row):
        if self.config_rank is None:
            rank = None
        else:
            fname, keys = self.config_rank
            rank = Functions.rank[fname](row, *keys)
        return rank

    def read_classes(self, row):
        # # TODO ???
        # return ['root', 'tree']
        return list({
            cls: None
            for fname, keys in self.config_classes
            for cls in Functions.classes[fname](row, *keys)
        })

    def read_data(self, row):
        return {
            destination: Functions.data[fname](row, *keys)
            for destination, (fname, keys) in self.config_data.items()
        }

