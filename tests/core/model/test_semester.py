import operator
from contextlib import nullcontext
from dataclasses import dataclass
from typing import ContextManager, Union

import pytest
from hypothesis import given, infer

from snutree.core.model.semester import Season, Semester
from tests.conftest import TestCase


@dataclass
class SeasonLessThanTestCase:
    a: Season
    b: Season
    expected: bool


@pytest.mark.parametrize(
    "case",
    [
        SeasonLessThanTestCase(
            a=Season.SPRING,
            b=Season.SPRING,
            expected=False,
        ),
        SeasonLessThanTestCase(
            a=Season.FALL,
            b=Season.FALL,
            expected=False,
        ),
        SeasonLessThanTestCase(
            a=Season.SPRING,
            b=Season.FALL,
            expected=True,
        ),
        SeasonLessThanTestCase(
            a=Season.FALL,
            b=Season.SPRING,
            expected=False,
        ),
    ],
)
def test_season_less_than(case: SeasonLessThanTestCase) -> None:
    assert (case.a < case.b) == case.expected


@given(season=infer, year=infer)  # type: ignore[misc]
def test_properties(season: Season, year: int) -> None:  # type: ignore[misc]
    """
    The actual season and year are not stored directly as fields, so we need to
    test that we can recover them correctly.
    """
    semester = Semester(season, year)
    assert (semester.season, semester.year) == (season, year)


@dataclass
class StrTestCase:
    semester: Semester
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        StrTestCase(Semester(Season.FALL, 2000), "Fall 2000"),
        StrTestCase(Semester(Season.SPRING, 2000), "Spring 2000"),
        StrTestCase(Semester(Season.FALL, -2000), "Fall -2000"),
    ],
)
def test_str(case: StrTestCase) -> None:
    assert str(case.semester) == case.expected


@dataclass
class FromStringTestCase(TestCase):
    string: str
    expected: Union[Semester, str]


@pytest.mark.parametrize(
    "case",
    [
        FromStringTestCase(
            id="normal",
            string="Fall 1999",
            expected=Semester(Season.FALL, 1999),
        ),
        FromStringTestCase(
            id="normal",
            string="Spring 1998",
            expected=Semester(Season.SPRING, 1998),
        ),
        FromStringTestCase(
            id="zeros",
            string="Fall 0",
            expected=Semester(Season.FALL, 0),
        ),
        FromStringTestCase(
            id="zeros",
            string="Fall 00000",
            expected=Semester(Season.FALL, 0),
        ),
        FromStringTestCase(
            id="zeros",
            string="Spring 000001",
            expected=Semester(Season.SPRING, 1),
        ),
        FromStringTestCase(
            id="zeros",
            string="Spring 001000",
            expected=Semester(Season.SPRING, 1000),
        ),
        FromStringTestCase(
            id="spaces",
            string="Spring1992",
            expected=Semester(Season.SPRING, 1992),
        ),
        FromStringTestCase(
            id="spaces",
            string="Fall1992",
            expected=Semester(Season.FALL, 1992),
        ),
        FromStringTestCase(
            id="spaces",
            string="       Spring   1992",
            expected=Semester(Season.SPRING, 1992),
        ),
        FromStringTestCase(
            id="case",
            string="fAlL 476",
            expected=Semester(Season.FALL, 476),
        ),
        FromStringTestCase(
            id="case",
            string="sPriNG 1453",
            expected=Semester(Season.SPRING, 1453),
        ),
        FromStringTestCase(
            id="invalid",
            string="sprig 1960",
            expected="Not a valid semester string: sprig 1960",
        ),
    ],
)
def test_from_string(case: FromStringTestCase) -> None:

    context: ContextManager[object]
    if isinstance(case.expected, str):
        context = pytest.raises(ValueError, match=case.expected)
    else:
        context = nullcontext()

    with context:
        assert Semester(case.string) == case.expected


@dataclass
class ReprTestCase:
    semester: Semester
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        ReprTestCase(
            semester=Semester("Fall 1990"),
            expected="Semester(season=<Season.FALL: 'Fall'>, year=1990)",
        ),
    ],
)
def test_repr(case: ReprTestCase) -> None:
    assert repr(case.semester) == case.expected


@given(index=infer)  # type: ignore[misc]
def test_index(index: int) -> None:  # type: ignore[misc]
    assert operator.index(Semester(index)) == index


@dataclass
class AdditionTestCase(TestCase):
    terms: Union[tuple[Semester, int], tuple[int, Semester]]
    expected: Semester


@pytest.mark.parametrize(
    "case",
    [
        AdditionTestCase(
            id="semester+integer",
            terms=(
                Semester(Season.FALL, 2015),
                1,
            ),
            expected=Semester(Season.SPRING, 2016),
        ),
        AdditionTestCase(
            id="semester+integer",
            terms=(
                Semester(Season.FALL, 2015),
                -1,
            ),
            expected=Semester(Season.SPRING, 2015),
        ),
        AdditionTestCase(
            id="semester+integer",
            terms=(
                Semester(Season.FALL, 2015),
                100,
            ),
            expected=Semester(Season.FALL, 2065),
        ),
        AdditionTestCase(
            id="integer+semester",
            terms=(
                1,
                Semester(Season.FALL, 2015),
            ),
            expected=Semester(Season.SPRING, 2016),
        ),
        AdditionTestCase(
            id="integer+semester",
            terms=(
                -1,
                Semester(Season.FALL, 2015),
            ),
            expected=Semester(Season.SPRING, 2015),
        ),
    ],
)
def test_addition(case: AdditionTestCase) -> None:

    if isinstance(case.terms[0], Semester):
        semester, integer = case.terms
    else:
        integer, semester = case.terms

    actual = semester + integer
    assert actual == case.expected
