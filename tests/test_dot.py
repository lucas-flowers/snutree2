from collections import OrderedDict
from nose.tools import assert_equals
from snutree.dot import Node, Edge, Rank, Graph
from inspect import cleandoc as trim


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

    # Sorting is necessary to ensure consistent equality checks with the output
    # string. The sorting key is the dict key.
    sorted_dict = lambda d : OrderedDict(sorted(d.items(), key=lambda t : t[0]))

    node1 = Node('Key One', sorted_dict({'label' : 'A Label', 'color' : 'piss yellow'}))
    node2 = Node('Key Two')

    edge = Edge(node1.key, node2.key)
    assert_equals(edge.to_dot(), '"Key One" -> "Key Two";')

    rank = Rank([node.key for node in (node1, node2)])

    subgraph = Graph(
            'something',
            'subgraph',
            [Node('S1', sorted_dict({'label' : 5})), Node('S2')],
            None,
            default_edge_attributes=sorted_dict({'label' : 'this'}),
            )

    graph = Graph(
            'tree',
            'digraph',
            [node1, edge, node2, subgraph, rank],
            sorted_dict({'size' : 5, 'width' : 'gold'}),
            sorted_dict({'width' : 4, 'penwidth' : '5'}),
            sorted_dict({'width' : 5, 'penwidth' : '4'}),
            )

    assert_equals(graph.to_dot(), trim('''
        digraph "tree" {
        size="5";
        width="gold";
        node [penwidth="5",width="4"];
        edge [penwidth="4",width="5"];
        "Key One" [color="piss yellow",label="A Label"];
        "Key One" -> "Key Two";
        "Key Two";
        subgraph "something" {
        edge [label="this"];
        "S1" [label="5"];
        "S2";
        }
        {rank=same "Key One" "Key Two"};
        }'''))

