import pytest
from snutree.utilities.tab import Tab

@pytest.mark.parametrize('tab, level, expected', [
    (Tab(tabstop=1, char='\t'), 0, ''),
    (Tab(tabstop=1, char='\t'), 1, '\t'),
    (Tab(tabstop=1, char='\t'), 2, '\t\t'),
    (Tab(tabstop=3, char='\t'), 1, '\t\t\t'),
    (Tab(tabstop=4, char='s'), 0, ''),
    (Tab(tabstop=4, char='s'), 1, 'ssss'),
    (Tab(tabstop=4, char='s'), 2, 'ssssssss'),
    (Tab(tabstop=2, char='ss'), 1, 'ssss'),
    (Tab(tabstop=4, char=' '), 0, ''),
    (Tab(tabstop=4, char=' '), 1, '    '),
    (Tab(tabstop=3, char=' '), 2, '      '),
    (Tab(tabstop=4, char=' '), 2, '        '),
    (Tab(tabstop=4, char=' '), 3, '            '),
])
def test_indent(tab, level, expected):
    for _ in range(level):
        tab.indent()
    assert str(tab) == expected

def test_indent_and_dedent():
    indent = Tab(tabstop=2, char='xxx')
    assert str(indent) == ''
    indent.indent()
    assert str(indent) == 'xxxxxx'
    indent.indent()
    assert str(indent) == 'xxxxxxxxxxxx'
    indent.dedent()
    assert str(indent) == 'xxxxxx'

def test_indented():
    indent = Tab(tabstop=2, char='xxx')
    assert str(indent) == ''
    indent.indent()
    assert str(indent) == 'xxxxxx'
    with indent.indented():
        assert str(indent) == 'xxxxxxxxxxxx'
    assert str(indent) == 'xxxxxx'
    indent.dedent()
    assert str(indent) == ''

