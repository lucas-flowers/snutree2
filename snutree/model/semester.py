import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import overload


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
    SEASON = rf"{Season.FALL}|{Season.SPRING}"
    SEMESTER = rf"\s*(?P<season>{SEASON})\s*(?P<year>{YEAR})\s*"
    PATTERN_SEMESTER = re.compile(SEMESTER, flags=re.IGNORECASE)

    @overload
    def __init__(self, index: int = ..., /) -> None: ...

    @overload
    def __init__(self, season: Season, year: int, /) -> None: ...

    @overload
    def __init__(self, string: str, /) -> None: ...

    def __init__(self, arg1: int | Season | str = 0, year: int | None = None) -> None:
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

            season_str: str = match.group("season")
            season = Season[season_str.upper()]

            year_str: str = match.group("year")
            year = int(year_str)

            self.__init__(season, year)  # type: ignore[misc] # pylint: disable=non-parent-init-called

            return

        object.__setattr__(self, "_index", index)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[object], "Semester"]]:
        yield cls.validate

    @classmethod
    def validate(cls, value: object) -> "Semester":
        if not isinstance(value, str):
            raise TypeError("string required")
        else:
            return cls(value)

    @property
    def year(self) -> int:
        return self._index // 2

    @property
    def season(self) -> Season:
        return Season.SPRING if self._index % 2 == 0 else Season.FALL

    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)!r})"

    def __str__(self) -> str:
        return f"{self.season} {self.year}"

    def __index__(self) -> int:
        return self._index
