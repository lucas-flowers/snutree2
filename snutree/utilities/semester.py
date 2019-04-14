
import re
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

@singledispatch
def _semester(value: int):
    return value

@_semester.register
def _(season: Season, year: int):
    return 2 * year + {Season.SPRING: 0, Season.FALL: 1}[season]

@_semester.register
def _(string: str):
    match = Semester.PATTERN_SEMESTER.match(string)
    return _semester( # pylint: disable=too-many-function-args
        getattr(Season, match.group('season').upper()),
        int(match.group('year')),
    )

class Semester(int):

    YEAR = r'\d+'
    SEASON = fr'{Season.FALL}|{Season.SPRING}'
    SEMESTER = fr'\s*(?P<season>{SEASON})\s*(?P<year>{YEAR})\s*'
    PATTERN_SEMESTER = re.compile(SEMESTER, flags=re.IGNORECASE)

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, _semester(*args, **kwargs))

    @property
    def year(self):
        return self // 2

    @property
    def season(self):
        return Season.SPRING if self % 2 == 0 else Season.FALL

    def __repr__(self):
        return f'{self.season} {self.year}'

    def __str__(self):
        return repr(self)

    def __add__(self, other):
        if isinstance(other, Semester):
            raise TypeError('Cannot add two semesters')
        else:
            return type(self)(super(type(self), self).__add__(other))

    __radd__ = __add__

