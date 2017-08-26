import string
import pytest
import snutree.schemas.sigmanu as sn

@pytest.mark.parametrize('MemberType', set(sn.MemberTypes.values()) - {sn.Reaffiliate})
def test_schema_agreement(MemberType):
    schema = MemberType.schema
    type_keys = set((s if isinstance(s, str) else s.schema) for s in schema.schema.keys())
    expected_keys = set(sn.description.keys())
    assert type_keys <= expected_keys

@pytest.mark.parametrize('latin, greek', sn.Affiliation.LATIN_TO_GREEK.items())
def test_unicode_latin(latin, greek):
    # Make sure the lookalike dict is set right (it's hard to tell)
    if latin not in ('(A)', '(B)'):
        assert latin in string.ascii_letters
        assert greek not in string.ascii_letters

@pytest.mark.parametrize('greek', sn.Affiliation.ENGLISH_TO_GREEK.values())
def test_unicode_english(greek):
    # Make sure the mapping dict is also set right
    assert greek not in string.ascii_letters

@pytest.mark.parametrize('acceptable, canonical', [
            # NOTE: The right side consists of /only/ Greek letters (i.e., 'Α' not 'A')
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
            ])
def test_constructor_string_success(acceptable, canonical):
    assert sn.Affiliation(acceptable) == sn.Affiliation(canonical)

@pytest.mark.parametrize('designation', [('A', 1), ('Beta Beta', 1234)])
def test_constructor_tuple_success(designation):
    # There should be no exceptions
    sn.Affiliation(*designation)

@pytest.mark.parametrize('designation', [
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
            ])
def test_constructor_value_failure(designation):
    with pytest.raises(ValueError):
        sn.Affiliation(designation)

@pytest.mark.parametrize('args', [
            ('Α', '1'),
            (1, 1),
            (1, '1'),
            (object(),),
            (1,),
            ])
def test_constructor_type_failure(args):
    # Invalid types for the constructor
    with pytest.raises(TypeError):
        sn.Affiliation(*args)

@pytest.mark.parametrize('chapter', ['A', 'Α', 'α', 'Alpha', 'alpha', 'AlPhA'])
@pytest.mark.parametrize('badge', ['123', '00000000123', 123])
@pytest.mark.parametrize('join', [True, False])
@pytest.mark.parametrize('expected', [sn.Affiliation('Α', 123)])
def test_constructor_consistency(expected, chapter, badge, join):
    if join:
        args = ('{chapter} {badge}'.format(chapter=chapter, badge=badge),)
    else:
        args = (chapter, int(badge))
    assert expected == sn.Affiliation(*args)

def test_sorting():
    # Sorting. Primary chapter goes first
    sn.SigmaNuMember.chapter = sn.Affiliation.str_to_designation('ΔA')
    a, c, b, d = tuple(sn.Affiliation(s) for s in ('ΔA 1', 'Α 2', 'ΔA 2', 'Ω 1'))
    assert sorted([a, c, b, d]) == [a, b, c, d]

