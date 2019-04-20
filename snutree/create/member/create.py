

from dataclasses import dataclass

from ...model.member import Member
from ...utilities import get
from .config import validate, parse_classes, parse_data

def read(rows, config=None):
    read = Read(config or {})
    return list(map(read.member, rows))

@dataclass
class Read:

    _classes: list
    _data: dict

    @classmethod
    def create(cls, config):
        validate(config)
        return cls(
            classes=parse_classes(get(config, 'classes')),
            data=parse_data(get(config, 'data')),
        )

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

