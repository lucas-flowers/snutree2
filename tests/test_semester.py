from itertools import permutations
from family_tree.semester import Semester

def test_comparisons():

    a = Semester('Fall 1900')
    b = Semester('Fall 1994')
    c = Semester('Spring 1995')
    d = Semester('Fall 1995')
    e = Semester('Fall 001995')
    f = Semester('Spring 3000')
    semesters = [a, b, c, d, e, f]

    # General
    for P in permutations(semesters):
        assert sorted(P) == semesters

    # Make sure total ordering worked
    assert b != c
    assert e > c
    assert e >= c
    assert e >= e

    # Min and max
    assert max(a, b, c) == c
    assert min(a, e, d) == a

def test_incdec():

    a = Semester('Fall 1995')
    a += 1
    a -= 1
    assert a == Semester('Fall 1995')

    b = Semester('Spring 1995')
    b += 1
    b -= 1
    assert b == Semester('Spring 1995')

def test_string():

    assert str(Semester('Fall 0001933')) == 'Fall 1933'
    assert str(Semester('Spring 323')) == 'Spring 323'

def test_math():

    assert isinstance(Semester('Fall 2001') + 8, Semester)
    assert str(Semester('Fall 2001') + 8) == 'Fall 2005'
    assert str(Semester('Fall 2001') + Semester('Spring 2001')) == 'Fall 4002'

