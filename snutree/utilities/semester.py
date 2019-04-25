
import re
from dataclasses import dataclass
from enum import Enum
from functools import singledispatch, total_ordering

@total_ordering
class Season(Enum):

    SPRING = 'Spring'
    FALL = 'Fall'

    def __str__(self):
        return self.value

    def __le__(self, other):
        return self == self.SPRING

@dataclass(init=False, order=True, frozen=True)
class Semester:

    _index: int

    YEAR = r'\d+'
    SEASON = fr'{Season.FALL}|{Season.SPRING}'
    SEMESTER = fr'\s*(?P<season>{SEASON})\s*(?P<year>{YEAR})\s*'
    PATTERN_SEMESTER = re.compile(SEMESTER, flags=re.IGNORECASE)

    def __init__(self, *args, **kwargs):

        @singledispatch
        def index(index: int):
            return index

        @index.register
        def _(season: Season, year: int):
            return 2 * year + {Season.SPRING: 0, Season.FALL: 1}[season]

        @index.register
        def _(string: str):
            match = type(self).PATTERN_SEMESTER.match(string)
            return index( # pylint: disable=too-many-function-args
                getattr(Season, match.group('season').upper()),
                int(match.group('year')),
            )

        # Extra fancy because this class is supposed to be frozen
        object.__setattr__(self, '_index', index(*args, **kwargs))

    @property
    def year(self):
        return self._index // 2

    @property
    def season(self):
        return Season.SPRING if self._index % 2 == 0 else Season.FALL

    def __repr__(self):
        return f'Semester(season={self.season!r}, year={self.year!r})'

    def __str__(self):
        return f'{self.season} {self.year}'

    def __index__(self):
        return self._index

    def __sub__(self, other):
        return Semester(self._index - other.__index__())

    def __add__(self, other):
        if isinstance(other, int):
            return Semester(self._index + other)
        else:
            raise TypeError('Can only add to int')

    __radd__ = __add__

