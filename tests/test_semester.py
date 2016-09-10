from nose.tools import *
from itertools import permutations
from family_tree.semester import Semester, semester_range

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
        assert_equals(sorted(P), semesters)

    # Make sure total ordering worked
    assert_not_equal(b, c)
    assert_greater(e, c)
    assert_greater_equal(e, c)
    assert_greater_equal(e, e)

    # Min and max
    assert_equals(max(a, b, c), c)
    assert_equals(min(a, e, d), a)

def test_incdec():

    a = Semester('Fall 1995')
    a += 1
    a -= 1
    assert_equals(a, Semester('Fall 1995'))

    b = Semester('Spring 1995')
    b += 1
    b -= 1
    assert_equals(b, Semester('Spring 1995'))

def test_string():

    assert_equals(str(Semester('Fall 0001933')), 'Fall 1933')
    assert_equals(str(Semester('Spring 323')), 'Spring 323')

def test_math():

    assert_is_instance(Semester('Fall 2001') + 8, Semester)
    assert_equals(str(Semester('Fall 2001') + 8), 'Fall 2005')
    assert_equals(str(8 + Semester('Fall 2001')), 'Fall 2005')
    assert_equals(str(Semester('Fall 2001') + Semester('Spring 2001')), 'Fall 4002')

def test_subtract():

    assert_equals(str(Semester('Fall 2001') - 1), 'Spring 2001')

def test_range():

    a = Semester('Fall 2000')
    b = Semester('Spring 2002')

    assert_equals(
            [str(s) for s in semester_range(a, b)],
            ['Fall 2000', 'Spring 2001', 'Fall 2001'],
            )

    assert_equals(
            list(semester_range(a, b)),
            [Semester(s) for s in ('Fall 2000', 'Spring 2001', 'Fall 2001')],
            )

