import re
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Optional, Union, overload


@total_ordering
class Season(Enum):

    SPRING = "Spring"
    FALL = "Fall"

    def __str__(self) -> str:
        return self.value

    def __le__(self, _other: "Season") -> bool:
        return self == self.SPRING  # type: ignore[comparison-overlap] # Mypy gets confused for some reason


@dataclass(init=False, order=True, frozen=True)
class Semester:

    _index: int

    YEAR = r"\d+"
    SEASON = fr"{Season.FALL}|{Season.SPRING}"
    SEMESTER = fr"\s*(?P<season>{SEASON})\s*(?P<year>{YEAR})\s*"
    PATTERN_SEMESTER = re.compile(SEMESTER, flags=re.IGNORECASE)

    @overload
    def __init__(self, index: int, /) -> None:
        ...

    @overload
    def __init__(self, season: Season, year: int, /) -> None:
        ...

    @overload
    def __init__(self, string: str, /) -> None:
        ...

    def __init__(self, arg1: Union[int, Season, str], year: Optional[int] = None) -> None:

        if isinstance(arg1, int):
            assert year is None
            index = arg1
        elif isinstance(arg1, Season):
            assert year is not None
            index = 2 * year + {Season.SPRING: 0, Season.FALL: 1}[arg1]
        else:
            assert year is None
            if not (match := self.PATTERN_SEMESTER.match(arg1)):
                raise ValueError(f"Not a valid semester string: {arg1}")
            season: Season = Season[match.group("season").upper()]
            year = int(match.group("year"))
            self.__init__(season, year)  # type: ignore[misc] # pylint: disable=non-parent-init-called
            return

        object.__setattr__(self, "_index", index)

    @property
    def year(self) -> int:
        return self._index // 2

    @property
    def season(self) -> Season:
        return Season.SPRING if self._index % 2 == 0 else Season.FALL

    def __repr__(self) -> str:
        return f"{type(self).__name__}(season={self.season!r}, year={self.year!r})"

    def __str__(self) -> str:
        return f"{self.season} {self.year}"

    def __index__(self) -> int:
        return self._index

    def __add__(self, other: int) -> "Semester":
        return type(self)(self._index + other)

    def __sub__(self, other: Union["Semester", int]) -> "Semester":
        if isinstance(other, Semester):
            return type(self)(self._index - other._index)
        else:
            return type(self)(self._index - other)
