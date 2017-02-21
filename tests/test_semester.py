from unittest import TestCase
from itertools import permutations
from snutree.semester import Semester

class TestSemester(TestCase):

    def setUp(self):

        self.a = Semester('Fall 1900')
        self.b = Semester('Fall 1994')
        self.c = Semester('Spring 1995')
        self.d = Semester('Fall 1995')
        self.e = Semester('Fall 001995')
        self.f = Semester('Spring 3000')
        self.semesters = [self.a, self.b, self.c, self.d, self.e, self.f]

    def test_sorting(self):

        for p in permutations(self.semesters):
            with self.subTest(p=p):
                self.assertEqual(sorted(p), self.semesters)

    def test_total_ordering(self):

        self.assertNotEqual(self.b, self.c)
        self.assertGreater(self.e, self.c)
        self.assertGreaterEqual(self.e, self.c)
        self.assertGreaterEqual(self.e, self.e)

    def test_min_max(self):

        self.assertEqual(max(self.a, self.b, self.c), self.c)
        self.assertEqual(min(self.a, self.e, self.d), self.a)

    def test_primitive(self):

        a = self.a
        a += 1
        self.assertIsNot(a, self.a)

    def test_inc_dec(self):

        a = self.a
        a += 1
        a -= 1
        self.assertEqual(a, self.a)

        b = self.b
        b += 1
        b -= 1
        self.assertEqual(b, self.b)

    def test_str(self):

        self.assertEqual(str(Semester('Fall 0001933')), 'Fall 1933')
        self.assertEqual(str(Semester('Spring 323')), 'Spring 323')

    def test_math(self):

        self.assertIsInstance(Semester('Fall 2001') + 8, Semester)
        self.assertEqual(str(Semester('Fall 2001') + 8), 'Fall 2005')
        self.assertEqual(str(8 + Semester('Fall 2001')), 'Fall 2005')
        self.assertEqual(str(Semester('Fall 2001') + Semester('Spring 2001')), 'Fall 4002')

    def test_subtract(self):

        self.assertEqual(str(Semester('Fall 2001') - 1), 'Spring 2001')

