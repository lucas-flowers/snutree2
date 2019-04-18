
import pytest

from snutree.write.member.config import Token, Parser, TokenError, ParseError

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
    ('a', 1),
    ('b', 2),
    ('c', 3),
    ('const()', 1337),
    ('neg(a)', -1),
    ('add(a, b)', 3),
    ('sub(c, a)', 2),
])
def test_parse(string, expected):
    row = {
        'a': 1,
        'b': 2,
        'c': 3,
    }
    functions = {
        'const': lambda: 1337,
        'neg': lambda x: -x,
        'add': lambda x, y: x + y,
        'sub': lambda x, y: x - y,
    }
    tokens = Token.tokenize(string)
    parser = Parser(functions)
    assert parser.parse(tokens)(row) == expected

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
def test_parse_error(string, expected):
    tokens = Token.tokenize(string)
    parser = Parser({})
    with pytest.raises(ParseError, match=expected):
        parser.parse(tokens)({})

