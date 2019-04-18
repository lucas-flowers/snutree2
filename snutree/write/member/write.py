
from dataclasses import dataclass

from ...model.member import Member
from ...utilities import get
from .config import validate, parse

def read(rows, config=None):
    read = Read(config or {})
    return list(map(read.member, rows))

@dataclass
class Read:

    config: dict

    @classmethod
    def from_dict(cls, dct):
        validate(dct)
        return cls(config=parse(dct))

    def member(self, row):
        return Member(
            data=self.data(row),
            classes=self.classes(row),
        )

    def data(self, row):
        return {
            fieldname: function(row)
            for fieldname, function in get(self.config, 'data').items()
        }

    def classes(self, row):
        return [
            # TODO?
            'root',
            'tree',
        ]

