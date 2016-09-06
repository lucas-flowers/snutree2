from itertools import permutations
from family_tree.semester import Semester

def test_comparisons():

    a = Semester('min')
    b = Semester('Fall 1994')
    c = Semester('Spring 1995')
    d = Semester('Fall 1995')
    e = Semester('Fall 001995')
    f = Semester('max')
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

    assert Semester('Fall 1995').decrement().increment() == Semester('Fall 1995')
    assert Semester('Spring 1995').decrement().increment() == Semester('Spring 1995')
    assert Semester('max').increment() == Semester('max')
    assert Semester('max').decrement() == Semester('max')
    assert Semester('min').increment() == Semester('min')
    assert Semester('min').decrement() == Semester('min')



