import pytest
from snutree.schemas.sigmanu import combine_names

@pytest.mark.parametrize('names, combined_name', [
    (('Jon', 'Freaking', 'Snow'), 'Freaking Snow'),
    (('Jon', 'Jonathan', 'Snow'), 'Jonathan Snow'),
    (('Jon', 'Snowy', 'Snow'), 'Jon Snow'),
    (('Jon', 'Snowball', 'Snow'), 'Jon Snow'),
    (('Samuel', 'Dick', 'Richards'), 'Dick Richards') # An unfortunate compromise
    ])
def test_combine_names(names, combined_name):
    assert combine_names(*names) == combined_name

@pytest.mark.parametrize('names, combined_name', [
    (('Jon', 'Snow', 'Snow'), 'Snow Snow')
    ])
def test_combine_names_not_equal(names, combined_name):
    assert combine_names(*names) != combined_name


