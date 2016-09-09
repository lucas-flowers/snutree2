import sys
from nose.tools import *
from family_tree.reading import *
from family_tree.node import *

def test_node():

    a = Node(0)
    b = Node(1)
    c = Node(2)
    d = Node(3)

    aa = Node(4)
    ab = Node(5)
    ac = Node(6)
    a.children = [aa, ab, ac]

    aba = Node(7)
    ab.children = [aba]

    e = Node(-1, [a, b, c, d])

    # Test iteration order
    for x, y in zip([x for x in e], [e, a, aa, ab, aba, ac, b, c, d]):
        assert_is(x, y)



def test_tree_from_records():

    records = read('directory.csv', 'chapters.csv', 'brothers_not_knights.csv')
    tree = tree_from_records(records)
    for node in tree:
        if node.record and node.record.key == '1352':
            assert_equal(
                sorted([child.record.name for child in node]),
                ['Aaron Magid', 'John Grezmak', 'Lucas Flowers', 'Tom Kan', 'Zach Palumbo'],
                )


