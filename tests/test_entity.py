from unittest import TestCase
import snutree.schemas.sigmanu as sn

class TestEntity(TestCase):

    def test_combine_names(self):

        self.assertEqual(sn.combine_names('Jon', 'Freaking', 'Snow'), 'Freaking Snow')
        self.assertEqual(sn.combine_names('Jon', 'Jonathan', 'Snow'), 'Jonathan Snow')
        self.assertEqual(sn.combine_names('Jon', 'Snowy', 'Snow'), 'Jon Snow')
        self.assertEqual(sn.combine_names('Jon', 'Snowball', 'Snow'), 'Jon Snow')

        # An unfortunate compromise
        self.assertEqual(sn.combine_names('Samuel', 'Dick', 'Richards'), 'Dick Richards')

        self.assertNotEqual(sn.combine_names('Jon', 'Snow', 'Snow'), 'Snow Snow')


