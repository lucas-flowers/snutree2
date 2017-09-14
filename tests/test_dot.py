from functools import partial
from itertools import product
from inspect import cleandoc as trim
import pytest
from snutree.utilities.dot import Defaults, Node, Edge, Rank, Graph
from snutree.utilities.indent import Indent

class TestAttributes:
    '''
    DOT attributes should be (shallow) copies of the attributes parameter,
    not just pointers.
    '''

    constructors = [
            partial(Graph, 1, 'graph'),
            partial(Defaults, 'node'),
            partial(Node, 2),
            partial(Edge, 3, 4)
            ]
    attributes = [{'blah' : 999}, {}, None]
    parameters = [(f(x), x) for f, x in product(constructors, attributes)]

    @pytest.mark.parametrize('entity, attributes', parameters)
    def test(self, entity, attributes):
        assert entity.attributes is not attributes

def test_Defaults():

    with pytest.raises(ValueError):
        Defaults('key', attributes={'label': 'A label'})

    defaults = Defaults('node', attributes={'label': 'A label'})
    assert str(defaults) == 'node [label="A label"];'

    indent = Indent(tabstop=3)
    indent.indent()
    assert defaults.to_dot(indent) == '   node [label="A label"];'

def test_Node():

    node = Node('A Key', {'label' : 'A Key Label'})
    assert str(node) == '"A Key" [label="A Key Label"];'

    node = Node('A Key')
    assert str(node) == '"A Key";'

def test_Edge():

    node1 = Node('Key One', {'label' : 'A Label'})
    node2 = Node('Key Two')

    edge = Edge(node1.key, node2.key)
    assert str(edge) == '"Key One" -> "Key Two";'

    edge = Edge(node1.key, node2.key, {'color' : 'white'})
    assert str(edge) == '"Key One" -> "Key Two" [color="white"];'

def test_Rank():

    rank = Rank(['a', 'b', 'c d'])
    assert str(rank) == '{rank=same "a" "b" "c d"};'

def test_Graph():

    node1 = Node('Key One', {'label' : 'A Label', 'color' : 'piss yellow'})
    node2 = Node('Key Two')

    edge = Edge(node1.key, node2.key)
    assert str(edge) == '"Key One" -> "Key Two";'

    rank = Rank([node.key for node in (node1, node2)])

    sub_edge_defaults = Defaults('edge', {'label': 'this'})

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

    assert graph.to_dot() == trim('''
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
        }''')

