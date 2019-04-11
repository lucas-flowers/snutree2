
import pytest

from snutree.sigmanu.affiliation import Affiliation

@pytest.mark.parametrize('string, expected', [

    # Basic abbreviated form
    ('Α 3', 'Α 3'),
    ('Π 5', 'Π 5'),
    ('ΔA 132', 'ΔΑ 132'),
    ('ABK 43925', 'ΑΒΚ 43925'),

    # All the sigmas
    ('Σςσ 5', 'ΣΣΣ 5'),

    # Mix of upper, lower, and lookalikes
    ('αKΚ 43925', 'ΑΚΚ 43925'),
    ('AαΑ(A)(a) 5', 'ΑΑΑ(A)(A) 5'),

    # Greek letters
    ('ΗΜ 5', 'ΗΜ 5'),

    # Latin letters
    ('HM 5', 'ΗΜ 5'),

    # Zero
    ('Α 0', 'Α 0'),
    ('Α 000000', 'Α 0'),
    ('Α 0000001', 'Α 1'),
    ('(A)(A) 0023', '(A)(A) 23'),

    # Basic English name
    ('Alpha 5', 'Α 5'),
    ('Delta Alpha 5', 'ΔΑ 5'),
    ('(A) (B) (A) (B) 234', '(A)(B)(A)(B) 234'),

    # Whitespace in a name
    ('        Alpha    \t    Beta\n\n\n      5    ', 'ΑΒ 5'),

    # Various cases in a name
    ('sigma Sigma SIGMA sIgMa 5', 'ΣΣΣΣ 5')

])
def test_Affiliation_from_string(string, expected):
    actual = str(Affiliation.from_string(string))
    assert actual == expected

@pytest.mark.parametrize('string', [

    # Empty string
    '',

    # Needs a designation
    '6',
    ' 6',

    # Needs a positive number
    'Α', # No number
    'A ', # No number
    'A -5', # No positive integer

    # Neither a Greek letter nor a lookalike
    'a 5',
    'D 5',
    '∏ 6', # Math pi product
    '∑ 6', # Math sigma sum

    # There is no '(C')
    'ΗΜ(C) 5', # There is no '(C)'
    'Eta Mu (C) 5', # There is no '(C)'

    # Cannot combine word form and character form
    'HM (A) 5',
    'Eta Mu(B) 5',
    '(B)(B) (B) 5',

])
def test_constructor_value_failure(string):
    with pytest.raises(AttributeError): # TODO Better error
        Affiliation.from_string(string)

