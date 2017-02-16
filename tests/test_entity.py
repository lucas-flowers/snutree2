from nose.tools import assert_equal, assert_not_equal
import snutree.entity as e

def test_combine_names():

    assert_equal(e.combine_names('Jon', 'Freaking', 'Snow'), 'Freaking Snow')
    assert_equal(e.combine_names('Jon', 'Jonathan', 'Snow'), 'Jonathan Snow')
    assert_equal(e.combine_names('Jon', 'Snowy', 'Snow'), 'Jon Snow')
    assert_equal(e.combine_names('Jon', 'Snowball', 'Snow'), 'Jon Snow')

    # An unfortunate compromise
    assert_equal(e.combine_names('Samuel', 'Dick', 'Richards'), 'Dick Richards')

    assert_not_equal(e.combine_names('Jon', 'Snow', 'Snow'), 'Snow Snow')


