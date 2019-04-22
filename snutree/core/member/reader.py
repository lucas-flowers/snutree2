
'''
Create Member objects from lists of rows.
'''

from functools import wraps

from ...utilities import get, name
from ...utilities.semester import Semester
from .config import validate
from .parser import Parser
from .model import Member

def read(rows, config=None):
    return Reader(config or {}).read_members(rows)

def read_row(row, config=None):
    return Reader(config or {}).read_member(row)

class FunctionNamespace:

    def __init__(self):
        self.mapping = {}

    def register(self, name):
        def wrapped(function):
            self.mapping[name] = function
            return staticmethod(function)
        return wrapped

    def __getitem__(self, value):
        return self.mapping[value]

class ClassFunctions:

    namespace = FunctionNamespace()

    @namespace.register(name=None)
    def default(keys, row):
        (key,) = keys
        return [row[key]]

    @namespace.register('Boolean')
    def boolean(keys, row):
        (key,) = keys
        value = row[key]
        if bool(value) and value.lower() in {'yes', 'true', '1'}:
            return [key]
        else:
            return []

    @namespace.register('List')
    def list(keys, row):
        (key,) = keys
        value = row[key]
        return [
            element.strip() for element
            in (value.split(',') if value.strip() else [])
        ]

class DataFunctions:

    namespace = FunctionNamespace()

    @namespace.register(name=None)
    def default(keys, row):
        (key,) = keys
        return row[key]

    @namespace.register('PreferredName')
    def preferred_name(keys, row):
        return name.preferred(*[row[key] for key in keys])

class RankFunctions:

    namespace = FunctionNamespace()

    @namespace.register('Semester')
    def semester(keys, row):
        (key,) = keys
        return Semester(row[key])

    @namespace.register('Integer')
    def integer(keys, row):
        (key,) = keys
        return int(row[key])

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
        return list(map(self.read_member, rows))

    def read_member(self, row):
        return Member(
            id=self.read_id(row),
            parent_id=self.read_parent_id(row),
            rank=self.read_rank(row),
            data=self.read_data(row),
            classes=self.read_classes(row),
        )

    def read_id(self, row):
        function_name, sources = self.config_id
        return DataFunctions.namespace[function_name](sources, row)

    def read_parent_id(self, row):
        function_name, sources = self.config_parent_id
        return DataFunctions.namespace[function_name](sources, row)

    def read_rank(self, row):
        if self.config_rank is None:
            rank = None
        else:
            function_name, sources = self.config_rank
            rank = RankFunctions.namespace[function_name](sources, row)
        return rank

    def read_classes(self, row):
        # # TODO ???
        # return ['root', 'tree']
        return list({
            cls: None
            for function_name, sources in self.config_classes
            for cls in ClassFunctions.namespace[function_name](sources, row)
        })

    def read_data(self, row):
        return {
            destination: DataFunctions.namespace[function_name](sources, row)
            for destination, (function_name, sources) in self.config_data.items()
        }

