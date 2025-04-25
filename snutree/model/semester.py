import re
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import assert_never, overload

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


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
        match arg1:
            case int():
                assert year is None
                index = arg1

            case Season():
                assert year is not None
                index = 2 * year + {Season.SPRING: 0, Season.FALL: 1}[arg1]

            case str():
                assert year is None

                if not (match := self.PATTERN_SEMESTER.match(arg1)):
                    raise ValueError(f"Not a valid semester string: {arg1}")

                season_str: str = match.group("season")
                season = Season[season_str.upper()]

                year_str: str = match.group("year")
                year = int(year_str)

                self.__init__(season, year)  # type: ignore[misc] # pylint: disable=non-parent-init-called

                return

            case _:
                assert_never(arg1)

        object.__setattr__(self, "_index", index)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: object, handler: GetCoreSchemaHandler) -> CoreSchema:
        schema: CoreSchema = core_schema.no_info_before_validator_function(cls, handler(Semester))
        return schema

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
