from unittest import TestCase
from snutree.dot import Defaults, Node, Edge, Rank, Graph
from inspect import cleandoc as trim

class TestDot(TestCase):

    def test_Defaults(self):

        self.assertRaises(ValueError, Defaults, 'key', attributes={'label': 'A label'})

        defaults = Defaults('node', attributes={'label': 'A label'})
        self.assertEquals(defaults.to_dot(), 'node [label="A label"];')
        self.assertEquals(defaults.to_dot(3), '            node [label="A label"];')

    def test_Node(self):

        node = Node('A Key', {'label' : 'A Key Label'})
        self.assertEquals(node.to_dot(), '"A Key" [label="A Key Label"];')

        node = Node('A Key')
        self.assertEquals(node.to_dot(), '"A Key";')

    def test_Edge(self):

        node1 = Node('Key One', {'label' : 'A Label'})
        node2 = Node('Key Two')

        edge = Edge(node1.key, node2.key)
        self.assertEquals(edge.to_dot(), '"Key One" -> "Key Two";')

        edge = Edge(node1.key, node2.key, {'color' : 'white'})
        self.assertEquals(edge.to_dot(), '"Key One" -> "Key Two" [color="white"];')

    def test_Rank(self):

        rank = Rank(['a', 'b', 'c d'])
        self.assertEquals(rank.to_dot(), '{rank=same "a" "b" "c d"};')

    def test_Graph(self):

        node1 = Node('Key One', {'label' : 'A Label', 'color' : 'piss yellow'})
        node2 = Node('Key Two')

        edge = Edge(node1.key, node2.key)
        self.assertEquals(edge.to_dot(), '"Key One" -> "Key Two";')

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

        self.assertEquals(graph.to_dot(), trim('''
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

