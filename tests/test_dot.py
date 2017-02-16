from nose.tools import assert_equals, assert_raises
from snutree.dot import Defaults, Node, Edge, Rank, Graph
from inspect import cleandoc as trim

def test_Defaults():

    assert_raises(ValueError, Defaults, 'key', attributes={'label' : 'A label'})

    defaults = Defaults('node', attributes={'label' : 'A label'})
    assert_equals(defaults.to_dot(), 'node [label="A label"];')
    assert_equals(defaults.to_dot(3), '            node [label="A label"];')

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

    node1 = Node('Key One', {'label' : 'A Label', 'color' : 'piss yellow'})
    node2 = Node('Key Two')

    edge = Edge(node1.key, node2.key)
    assert_equals(edge.to_dot(), '"Key One" -> "Key Two";')

    rank = Rank([node.key for node in (node1, node2)])

    sub_edge_defaults = Defaults('edge', {'label' : 'this'})

    subgraph = Graph(
            'something',
            'subgraph',
            children=[sub_edge_defaults, Node('S1', {'label' : 5}), Node('S2')],
            )

    node_defaults = Defaults('node', {'width' : 4, 'penwidth' : '5'})
    edge_defaults = Defaults('edge', {'width' : 5, 'penwidth' : '4'})

    graph = Graph(
            'tree',
            'digraph',
            attributes={'size' : 5, 'width' : 'gold'},
            children=[node_defaults, edge_defaults, node1, edge, node2, subgraph, rank],
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

