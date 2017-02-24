from unittest import TestCase
from snutree.utilities import combine_names

class TestCombineNames(TestCase):

    def test_combine_names(self):

        self.assertEqual(combine_names('Jon', 'Freaking', 'Snow'), 'Freaking Snow')
        self.assertEqual(combine_names('Jon', 'Jonathan', 'Snow'), 'Jonathan Snow')
        self.assertEqual(combine_names('Jon', 'Snowy', 'Snow'), 'Jon Snow')
        self.assertEqual(combine_names('Jon', 'Snowball', 'Snow'), 'Jon Snow')

        # An unfortunate compromise
        self.assertEqual(combine_names('Samuel', 'Dick', 'Richards'), 'Dick Richards')

        self.assertNotEqual(combine_names('Jon', 'Snow', 'Snow'), 'Snow Snow')

