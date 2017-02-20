import string
import nose.tools as nt
from snutree.schemas.sigmanu import Affiliation

def test_affiliation():

    # IMPORTANT NOTE: The letters we are testing against

    # Make sure the lookalike dict is set right (it's hard to tell)
    for latin, greek in Affiliation.LATIN_TO_GREEK.items():
        if latin not in ('(A)', '(B)'):
            nt.assert_in(latin, string.ascii_letters)
            nt.assert_not_in(greek, string.ascii_letters)

    # Make sure the mapping dict is also set right
    for greek in Affiliation.ENGLISH_TO_GREEK.values():
        nt.assert_not_in(greek, string.ascii_letters)

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
        nt.assert_equals(Affiliation(i), Affiliation(o))

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
            ]

    for f in failed_designations:
        nt.assert_raises(ValueError, Affiliation, f)

    # Not a string
    nt.assert_raises(TypeError, Affiliation, object())

