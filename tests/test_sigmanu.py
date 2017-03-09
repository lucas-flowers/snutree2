import string
from unittest import TestCase
import snutree.member.sigmanu as sn

class TestSigmaNu(TestCase):

    def test_schema_agreement(self):

        for MemberType in set(sn.MemberTypes.values()) - {sn.Reaffiliate}:
            schema = MemberType.schema
            with self.subTest(schema=schema):
                type_keys = set((s if isinstance(s, str) else s.schema)
                    for s in schema.schema.keys())
                expected_keys = set(sn.schema_information().keys())
                self.assertTrue(type_keys <= expected_keys)

class TestAffiliation(TestCase):

    def test_unicode_latin(self):

        # Make sure the lookalike dict is set right (it's hard to tell)
        for latin, greek in sn.Affiliation.LATIN_TO_GREEK.items():
            if latin not in ('(A)', '(B)'):
                self.assertIn(latin, string.ascii_letters)
                self.assertNotIn(greek, string.ascii_letters)

    def test_unicode_english(self):

        # Make sure the mapping dict is also set right
        for greek in sn.Affiliation.ENGLISH_TO_GREEK.values():
            self.assertNotIn(greek, string.ascii_letters)

    def test_constructor_string_success(self):

        # Input designation on the left; canonical designation on the right.
        # NOTE: The right side consists of /only/ Greek letters (i.e., 'Α' not 'A')
        designations = [

                # Greek-letter designations (beware of lookalikes)
                ('ΔA 132', 'ΔΑ 132'),
                ('Α 3', 'Α 3'),
                ('Α 0', 'Α 0'),
                ('ΗΜ(A) 5', 'ΗΜ(A) 5'), # Greek input
                ('HM(A) 5', 'ΗΜ(A) 5'), # Latin input
                ('(A)(A) 0023', '(A)(A) 23'), # Padded zeroes
                ('ABK 43925', 'ΑΒΚ 43925'),
                ('αKΚ 43925', 'AΚΚ 43925'),
                ('AαΑ(A)(a) 5', 'ΑΑΑ(A)(A) 5'), # Mix of upper, lower, and lookalikes
                ('Σςσ 5', 'ΣΣΣ 5'), # All the Sigmas
                ('Π 5', 'Π 5'),

                # English name designations
                ('Delta Alpha 5', 'ΔΑ 5'),
                ('        Alpha    \t    Beta\n\n\n      5    ', 'ΑΒ 5'), # Whitespace
                ('Alpha 5', 'Α 5'),
                ('(A) (B) (A) (B) 234', '(A)(B)(A)(B) 234'),
                ('sigma Sigma SIGMA sIgMa 5', 'ΣΣΣΣ 5') # Various cases

                ]

        for i, o in designations:
            with self.subTest(i=i, o=o):
                self.assertEqual(sn.Affiliation(i), sn.Affiliation(o))

    def test_constructor_tuple_success(self):

        designations = [
                ('A', 1),
                ('Beta Beta', 1234)
                ]

        for designation in designations:
            with self.subTest(designation=designation):
                try:
                    sn.Affiliation(*designation)
                except Exception as exception:
                    msg = f'Unexpected exception for {designation!r}: {exception}'
                    self.fail(msg)

    def test_constructor_value_failure(self):

        failed_designations = [
                'a 5', # 'a' is not Greek, nor a Greek lookalike
                'D 5', # Same with 'D'
                'Eta Mu(B) 5', # Needs space before '(B)'
                'Eta Mu (C) 5', # No (C); only (A) and (B)
                'HM (A) 5', # Must have no space before (A)
                '(B)(B) (B) 5', # Must either be '(B) (B) (B)' ("words") or '(B)(B)(B)' ("letters")
                'Α', # No number
                'A ', # No number
                'A -5', # No positive integer
                'ΗΜ(C) 5', # No (C); only (A) and (B)
                '∏ 6', # Wrong pi (that's the product pi)
                '∑ 6', # Wrong sigma (that's the sum sigma)
                '6', # No designation
                ' 6', # No designation
                '', # Empty string
                ]

        for f in failed_designations:
            with self.subTest(f=f):
                self.assertRaises(ValueError, sn.Affiliation, f)

    def test_constructor_type_failure(self):

        # Failed constructor types
        failed_types = [
                ('Α', '1'),
                (1, 1),
                (1, '1'),
                (object(),),
                (1,),
                ]
        for f in failed_types:
            with self.subTest(f=f):
                self.assertRaises(TypeError, sn.Affiliation, *f)

    def test_sorting(self):

        # Sorting. Primary chapter (default is 'ΔΑ') goes first
        a, c, b, d = tuple(sn.Affiliation(s) for s in ('ΔA 1', 'Α 2', 'ΔA 2', 'Ω 1'))
        self.assertEqual(sorted([a, c, b, d]), [a, b, c, d])

