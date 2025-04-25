
import pytest

from snutree.utilities.semester import Semester, Season

@pytest.mark.parametrize('season, year', [
    (Season.FALL, 1970),
    (Season.SPRING, 1970),
    (Season.FALL, 1971),
    (Season.SPRING, 1971),
])
def test_properties(season, year):
    '''
    The actual season and year are not stored directly as fields, so we need to
    test that we can recover them correctly.
    '''
    semester = Semester(season, year)
    assert (semester.season, semester.year) == (season, year)

@pytest.mark.parametrize('semester, expected', [
    (Semester(Season.FALL, 2000), 'Fall 2000'),
    (Semester(Season.SPRING, 2000), 'Spring 2000'),
    (Semester(Season.FALL, -2000), 'Fall -2000'),
])
def test_str(semester, expected):
    assert str(semester) == expected

@pytest.mark.parametrize('string, expected', [

    # Normal
    ('Fall 1999', Semester(Season.FALL, 1999)),
    ('Spring 1998', Semester(Season.SPRING, 1998)),

    # Zeros
    ('Fall 0', Semester(Season.FALL, 0)),
    ('Fall 00000', Semester(Season.FALL, 0)),
    ('Spring 000001', Semester(Season.SPRING, 1)),
    ('Spring 001000', Semester(Season.SPRING, 1000)),

    # Spaces
    ('Spring1992', Semester(Season.SPRING, 1992)),
    ('Fall1992', Semester(Season.FALL, 1992)),
    ('       Spring   1992', Semester(Season.SPRING, 1992)),

    # Case
    ('fAlL 476', Semester(Season.FALL, 476)),
    ('sPriNG 1453', Semester(Season.SPRING, 1453)),

])
def test_from_string(string, expected):
    assert Semester(string) == expected

@pytest.mark.parametrize('a, b, expected', [

    # Semester plus integer
    (Semester(Season.FALL, 2015), 1, Semester(Season.SPRING, 2016)),
    (Semester(Season.FALL, 2015), -1, Semester(Season.SPRING, 2015)),
    (Semester(Season.FALL, 2015), 100, Semester(Season.FALL, 2065)),

    # Integer plus semester
    (1, Semester(Season.FALL, 2015), Semester(Season.SPRING, 2016)),
    (-1, Semester(Season.FALL, 2015), Semester(Season.SPRING, 2015)),

])
def test_addition(a, b, expected):
    actual = a + b
    assert actual == expected
    assert isinstance(actual, Semester)

def test_addition_invalid():
    '''
    Cannot add semesters together.
    '''
    with pytest.raises(TypeError):
        Semester(Season.FALL, 1000) + Semester(Season.SPRING, 1001)

