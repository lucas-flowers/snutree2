
import pytest

from snutree.core.member.parser import Token, Parser, TokenError, ParseError
from snutree.utilities.semester import Semester

@pytest.mark.parametrize('string, expected', [

    ('sin', [
        Token('IDENTIFIER', 'sin'),
    ]),

    ('cos(x)', [
        Token('IDENTIFIER', 'cos'),
        Token('OPEN_BRACKET', '('),
        Token('IDENTIFIER', 'x'),
        Token('CLOSE_BRACKET', ')'),
    ]),

    (' tan ( y ) ', [
        Token('IDENTIFIER', 'tan'),
        Token('OPEN_BRACKET', '('),
        Token('IDENTIFIER', 'y'),
        Token('CLOSE_BRACKET', ')'),
    ]),

    (' exp(x, y, z) ', [
        Token('IDENTIFIER', 'exp'),
        Token('OPEN_BRACKET', '('),
        Token('IDENTIFIER', 'x'),
        Token('COMMA', ','),
        Token('IDENTIFIER', 'y'),
        Token('COMMA', ','),
        Token('IDENTIFIER', 'z'),
        Token('CLOSE_BRACKET', ')'),
    ]),

])
def test_tokenize(string, expected):
    assert list(Token.tokenize(string)) == expected

@pytest.mark.parametrize('string', [
    '-',
    'function(x; y)',
    'function[x; y]',
])
def test_tokenize_error(string):
    with pytest.raises(TokenError):
        list(Token.tokenize(string))

@pytest.mark.parametrize('string, expected', [

    # Simple
    ('a', (None, ['a'])),
    ('b', (None, ['b'])),
    ('c', (None, ['c'])),

    # Zero-parameter function
    ('const()', ('const', [])),

    # One-parameter function
    ('neg(a)', ('neg', ['a'])),

    # Two-parameter functions
    ('add(a, b)', ('add', ['a', 'b'])),
    ('sub(c, a)', ('sub', ['c', 'a'])),

])
def test_parse(string, expected):
    function_name, field_names = Parser().parse(string)
    assert (function_name, list(field_names)) == expected

@pytest.mark.parametrize('string, expected', [
    ('', 'end of input'),
    ('(', 'IDENTIFIER'),
    ('identifier0 identifier1', 'OPEN_BRACKET'),
    ('function(', 'CLOSE_BRACKET'),
    ('function(x y', 'CLOSE_BRACKET'),
    ('function(x y)', 'CLOSE_BRACKET'),
    ('function(,)', 'IDENTIFIER'),
    ('function(x,)', 'IDENTIFIER'),
])
def test_parser_parse_error(string, expected):
    parser = Parser()
    with pytest.raises(ParseError, match=expected):
        parser.parse(string)

