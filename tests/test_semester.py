from itertools import permutations
import pytest
from snutree.utilities.semester import Semester

a = Semester('Fall 1900')
b = Semester('Fall 1994')
c = Semester('Spring 1995')
d = Semester('Fall 1995')
e = Semester('Fall 001995')
f = Semester('Spring 3000')

@pytest.mark.parametrize('p', permutations([a, b, c, d]))
def test_sorting(p):
    assert sorted(p) == [a, b, c, d]

def test_total_ordering():
    assert b != c
    assert e  > c
    assert e >= c
    assert e >= e

def test_min_max():
    assert max(a, b, c) == c
    assert min(a, e, d) == a

def test_primitive():
    new_a = a
    new_a += 1
    assert new_a is not a

def test_inc_dec():
    new_a = a
    new_a += 1
    new_a -= 1
    assert new_a == a
    new_b = b
    new_b += 1
    new_b -= 1
    assert new_b == b

def test_str():
    assert str(Semester('Fall 0001933')) == 'Fall 1933'
    assert str(Semester('Spring 323')) == 'Spring 323'

def test_math():
    assert isinstance(Semester('Fall 2001') + 8, Semester)
    assert str(Semester('Fall 2001') + 8) == 'Fall 2005'
    assert str(8 + Semester('Fall 2001')) == 'Fall 2005'
    assert str(Semester('Fall 2001') + Semester('Spring 2001')) == 'Fall 4002'

def test_subtract():
    assert str(Semester('Fall 2001') - 1) == 'Spring 2001'

