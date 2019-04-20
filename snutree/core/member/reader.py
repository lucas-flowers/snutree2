
'''
Create Member objects from lists of rows.
'''

from dataclasses import dataclass

from ...utilities import get
from .config import validate, parse_classes, parse_data
from .model import Member

def read(rows, config=None):
    return Reader(config or {}).read(rows)

@dataclass
class Reader:

    _classes: list
    _data: dict

    @classmethod
    def create(cls, config):
        validate(config)
        return cls(
            classes=parse_classes(get(config, 'classes')),
            data=parse_data(get(config, 'data')),
        )

    def read(self, rows):
        return list(map(self.member, rows))

    def member(self, row):
        return Member(
            data=self.data(row),
            classes=self.classes(row),
        )

    def data(self, row):
        return {
            fieldname: function(row)
            for fieldname, function in self._data.items()
        }

    def classes(self, row):
        return [
            # TODO?
            'root',
            'tree',
        ]

