
'''
Parse functions that map row fields to data fields and classes.
'''

import re
from contextlib import contextmanager
from dataclasses import dataclass

class TokenError(Exception):
    pass

class ParseError(Exception):
    pass

@dataclass
class Token:

    kind: str
    value: str

    TOKENS = {
        'IDENTIFIER': r'(?i:[_a-z][_a-z0-9]*)',
        'OPEN_BRACKET': r'[(]',
        'CLOSE_BRACKET': r'[)]',
        'COMMA': r'[,]',
        'WHITESPACE': r'[ \t\n]+',
        'UNKNOWN': r'.',
    }

    TOKEN_PATTERN = re.compile('|'.join(
        fr'(?P<{name}>{regex})' for name, regex in TOKENS.items()
    ))

    @classmethod
    def tokenize(cls, string):
        for match in cls.TOKEN_PATTERN.finditer(string):
            kind, value = match.lastgroup, match.group()
            if kind == 'WHITESPACE':
                continue
            elif kind == 'UNKNOWN':
                raise TokenError(f'Unknown character: {value!r}')
            else:
                yield cls(kind, value)

class Parser:

    def __init__(self):
        self._first_token = None
        self._rest_tokens = None

    @contextmanager
    def load(self, tokens):

        if not (self._first_token is None and self._rest_tokens is None):
            raise ParseError('Parsing already in progress')

        self._rest_tokens = iter(tokens)
        self.next()
        yield self
        self._first_token = None

    def next(self):
        try:
            next_token = self._first_token
            self._first_token = next(self._rest_tokens)
        except StopIteration:
            self._first_token = None
            self._rest_tokens = None
        return next_token

    def has_next(self):
        return self._first_token is not None and self._rest_tokens is not None

    def lookahead(self):
        return self._first_token

    def expect(self, literal):
        token = self.next() if self.has_next() else None
        if token is None:
            raise ParseError(f'Expected {literal} but found end of input')
        elif token.kind == literal:
            return token
        else:
            raise ParseError(f'Expected {literal} but found: {token.value!r}')

    def parse(self, string):
        return self.parse_tokens(Token.tokenize(string))

    def parse_tokens(self, tokens):
        with self.load(tokens):
            return self.expression()

    def expression(self):
        '''
        expression : IDENTIFIER application
                   | IDENTIFIER
        '''
        identifier = self.expect('IDENTIFIER').value
        args = list(self.application()) if self.has_next() else None
        if args is None:
            function_name, field_names = None, [identifier]
        else:
            function_name, field_names = identifier, args
        return (function_name, field_names)

    def application(self):
        '''
        application : '(' arguments ')'
                    | '(' ')'
        '''
        self.expect('OPEN_BRACKET')
        if self.has_next() and self.lookahead().kind != 'CLOSE_BRACKET':
            yield from self.arguments()
        self.expect('CLOSE_BRACKET')

    def arguments(self):
        '''
        arguments : argument arguments_tail
        '''
        yield self.argument()
        yield from self.arguments_tail()

    def arguments_tail(self):
        '''
        arguments_tail : ',' argument arguments_tail
                       | e
        '''
        if self.has_next() and self.lookahead().kind == 'COMMA':
            self.expect('COMMA')
            yield self.argument()
            yield from self.arguments_tail()

    def argument(self):
        '''
        argument : IDENTIFIER
        '''
        return self.expect('IDENTIFIER').value

