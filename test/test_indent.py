import pytest
from snutree.utilities.indent import Indent

@pytest.mark.parametrize('expected, indent, level', [
    ('', Indent(tabstop=1, char='\t'), 0),
    ('\t', Indent(tabstop=1, char='\t'), 1),
    ('\t\t', Indent(tabstop=1, char='\t'), 2),
    ('', Indent(tabstop=4, char='s'), 0),
    ('ssss', Indent(tabstop=4, char='s'), 1),
    ('ssssssss', Indent(tabstop=4, char='s'), 2),
    ('\t\t\t', Indent(tabstop=3, char='\t'), 1),
    ('ssss', Indent(tabstop=2, char='ss'), 1),
    ('ssss', Indent(tabstop=2, char='ss'), 1),
    ('', Indent(), 0),
    ('    ', Indent(), 1),
    ('        ', Indent(), 2),
    ('            ', Indent(), 3),
    ('      ', Indent(tabstop=3), 2),
    ])
def test_Indent(expected, indent, level):
    for _ in range(level):
        indent.indent()
    assert str(indent) == expected

def test_Dedent():
    indent = Indent(tabstop=2, char='xxx')
    assert str(indent) == ''
    indent.indent()
    assert str(indent) == 'xxxxxx'
    indent.indent()
    assert str(indent) == 'xxxxxxxxxxxx'
    indent.dedent()
    assert str(indent) == 'xxxxxx'

def test_Indented():
    indent = Indent(tabstop=2, char='xxx')
    assert str(indent) == ''
    indent.indent()
    assert str(indent) == 'xxxxxx'
    with indent.indented():
        assert str(indent) == 'xxxxxxxxxxxx'
    assert str(indent) == 'xxxxxx'
    indent.dedent()
    assert str(indent) == ''

