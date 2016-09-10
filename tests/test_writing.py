import sys
from nose.tools import *
from family_tree.writing import *

def test_Node():

    node = Node('A Key', {'label' : 'A Key Label'})
    assert_equals(node.to_dot(), '"A Key" [label="A Key Label"];')

    node = Node('A Key')
    assert_equals(node.to_dot(), '"A Key";')

def test_Edge():

    node1 = Node('Key One', {'label' : 'A Label'})
    node2 = Node('Key Two')

    edge = Edge(node1.key, node2.key)
    assert_equals(edge.to_dot(), '"Key One" -> "Key Two";')

    edge = Edge(node1.key, node2.key, {'color' : 'white'})
    assert_equals(edge.to_dot(), '"Key One" -> "Key Two" [color="white"];')

def test_Rank():

    rank = Rank(['a', 'b', 'c d'])
    assert_equals(rank.to_dot(), '{rank=same "a" "b" "c d"};')

def test_Graph():

    node1 = Node('Key One', {'label' : 'A Label'})
    node2 = Node('Key Two')

    edge = Edge(node1.key, node2.key)
    assert_equals(edge.to_dot(), '"Key One" -> "Key Two";')

    rank = Rank([node.key for node in (node1, node2)])

    graph = Graph(
            'tree',
            'digraph',
            [node1, edge, node2, rank],
            {'size' : 5, 'width' : 'gold'},
            )

    print(graph.to_dot(), file=sys.stderr)



