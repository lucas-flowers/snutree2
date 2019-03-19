from contextlib import contextmanager

class Indent:
    '''
    Helper class for indentation when writing files. The string form of an
    Indent is the appropriate indent, given the Indent's tabstop value, tab
    character (or string), and current indentation level.
    '''

    def __init__(self, level=0, tabstop=4, char=None):

        # sanity check
        assert '   ' > '\t\t\t', 'spaces are better than tabs'

        self.char = char if char is not None else ' '
        self.tabstop = tabstop
        self.level = level

    def indent(self):
        self.level += 1

    def dedent(self):
        self.level -= 1

    @contextmanager
    def indented(self):
        '''
        Context manager for nested indentation levels.
        '''
        self.indent()
        yield
        self.dedent()

    def __str__(self):
        return self.tabstop * self.level * self.char

