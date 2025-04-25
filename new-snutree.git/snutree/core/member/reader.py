
'''
Create Member objects from lists of rows.
'''

from dataclasses import dataclass

from ...utilities import name
from ...utilities.semester import Semester
from .config import Config
from .model import Member
from .parser import Parser

def read(rows, config: dict):
    config = Config.from_dict(config)
    return Reader(config).read_members(rows)

def read_row(row, config: dict):
    config = Config.from_dict(config)
    return Reader(config).read_member(row)

class Functions:

    class FunctionNamespace(dict):
        def register(self, name):
            def wrapped(function):
                self[name] = function
                return staticmethod(function)
            return wrapped

    rank = FunctionNamespace()

    @rank.register('Integer')
    def integer(row, key) -> int:
        return int(row[key])

    @rank.register('Semester')
    def semester(row, key) -> Semester:
        return Semester(row[key])

    classes = FunctionNamespace()

    @classes.register(name=None)
    def constant(row, constant):
        return [constant]

    @classes.register('Boolean')
    def boolean(row, key):
        value = row[key]
        if bool(value) and value.lower() in {'yes', 'true', '1'}:
            return [key]
        else:
            return []

    @classes.register('Enum')
    def enum(row, key):
        return [row[key]]

    @classes.register('List')
    def list(row, key):
        value = row[key]
        return [
            element.strip()
            for element in (value.split(',') if value.strip() else [])
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

@dataclass
class Reader:

    parser = Parser()

    config: Config

    @property
    def Rank(self):
        fname, _ = self.config.rank
        function = Functions.rank[fname]
        constructor = function.__annotations__['return']
        return constructor

    def read_id(self, row):
        fname, keys = self.config.id
        return Functions.data[fname](row, *keys)

    def read_parent_id(self, row):
        fname, keys = self.config.parent_id
        return Functions.data[fname](row, *keys)

    def read_rank(self, row):
        if self.config.rank is None:
            rank = None
        else:
            fname, keys = self.config.rank
            rank = Functions.rank[fname](row, *keys)
        return rank

    def read_classes(self, row):
        return list({
            cls: None # Using dict to maintain both order and uniqueness
            for fname, keys in self.config.classes
            for cls in Functions.classes[fname](row, *keys)
        })

    def read_data(self, row):
        return {
            destination: Functions.data[fname](row, *keys)
            for destination, (fname, keys) in self.config.data.items()
        }

    def read_member(self, row):
        return Member(
            id=self.read_id(row) if self.config.id else None,
            parent_id=self.read_parent_id(row) if self.config.parent_id else None,
            rank=self.read_rank(row) if self.config.rank else None,
            classes=self.read_classes(row),
            data=self.read_data(row),
        )

    def read_custom_member(self, row):
        return Member(
            id=row['id'],
            parent_id=row['parent_id'],
            rank=self.Rank(row['rank']) if self.config.rank is not None else None,
            data=row['data'],
            classes=row['classes'],
        )

    def read_members(self, rows):
        return [
            *map(self.read_member, rows),
            *map(self.read_custom_member, self.config.custom),
        ]

