import nose.tools as nt
from itertools import permutations
from snutree.semester import Semester

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
        nt.assert_equals(sorted(P), semesters)

    # Make sure total ordering worked
    nt.assert_not_equal(b, c)
    nt.assert_greater(e, c)
    nt.assert_greater_equal(e, c)
    nt.assert_greater_equal(e, e)

    # Min and max
    nt.assert_equals(max(a, b, c), c)
    nt.assert_equals(min(a, e, d), a)

def test_incdec():

    a = Semester('Fall 1995')
    a += 1
    a -= 1
    nt.assert_equals(a, Semester('Fall 1995'))

    b = Semester('Spring 1995')
    b += 1
    b -= 1
    nt.assert_equals(b, Semester('Spring 1995'))

def test_string():

    nt.assert_equals(str(Semester('Fall 0001933')), 'Fall 1933')
    nt.assert_equals(str(Semester('Spring 323')), 'Spring 323')

def test_math():

    nt.assert_is_instance(Semester('Fall 2001') + 8, Semester)
    nt.assert_equals(str(Semester('Fall 2001') + 8), 'Fall 2005')
    nt.assert_equals(str(8 + Semester('Fall 2001')), 'Fall 2005')
    nt.assert_equals(str(Semester('Fall 2001') + Semester('Spring 2001')), 'Fall 4002')

def test_subtract():

    nt.assert_equals(str(Semester('Fall 2001') - 1), 'Spring 2001')

