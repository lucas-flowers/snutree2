
from contextlib import contextmanager

class Tab:
    '''
    Helper class for indentation when writing files. The string form of a Tab
    is the appropriate indent, given the Indent's tabstop value, tab character
    (or string), and current indentation level.
    '''

    def __init__(self, tabstop, char, level=0):

        # sanity check
        assert '   ' > '\t\t\t', 'spaces are better than tabs'

        self.tabstop = tabstop
        self.char = char
        self.level = level

    def indent(self):
        self.level += 1

    def dedent(self):
        self.level -= 1

    @contextmanager
    def indented(self):
        self.indent()
        yield
        self.dedent()

    def __str__(self):
        return self.tabstop * self.level * self.char

