from unittest import TestCase
from snutree.indent import Indent

class TestIndent(TestCase):

    def test_Indent(self):

        tests = [
                ('', Indent(tabstop=1, char='\t'), 0),
                ('\t', Indent(tabstop=1, char='\t'), 1),
                ('\t\t', Indent(tabstop=1, char='\t'), 2),
                ('', Indent(tabstop=4, char='s'), 0),
                ('ssss', Indent(tabstop=4, char='s'), 1),
                ('ssssssss', Indent(tabstop=4, char='s'), 2),
                ('\t\t\t', Indent(3, '\t'), 1),
                ('ssss', Indent(tabstop=2, char='ss'), 1),
                ('ssss', Indent(2, 'ss'), 1),
                ('', Indent(), 0),
                ('    ', Indent(), 1),
                ('        ', Indent(), 2),
                ('            ', Indent(), 3),
                ('      ', Indent(3), 2),
                ]

        for expected, indent, level in tests:
            with self.subTest(expected=expected, indent=indent, level=level):
                for _ in range(level):
                    indent.indent()
                self.assertEqual(expected, str(indent))

    def test_Dedent(self):
        indent = Indent(tabstop=2, char='xxx')
        self.assertEqual('', str(indent))
        indent.indent()
        self.assertEqual('xxxxxx', str(indent))
        indent.indent()
        self.assertEqual('xxxxxxxxxxxx', str(indent))
        indent.dedent()
        self.assertEqual('xxxxxx', str(indent))

    def test_Indented(self):
        indent = Indent(tabstop=2, char='xxx')
        self.assertEqual('', str(indent))
        indent.indent()
        self.assertEqual('xxxxxx', str(indent))
        with indent.indented():
            self.assertEqual('xxxxxxxxxxxx', str(indent))
        self.assertEqual('xxxxxx', str(indent))
        indent.dedent()
        self.assertEqual('', str(indent))

