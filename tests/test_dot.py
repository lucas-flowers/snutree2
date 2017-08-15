from unittest import TestCase
from inspect import cleandoc as trim
from snutree.dot import Defaults, Node, Edge, Rank, Graph
from snutree.indent import Indent

class TestDot(TestCase):

    maxDiff = None

    def test_attributes(self):
        '''
        DOT attributes should be (shallow) copies of the attributes parameter,
        not just pointers.
        '''

        for attributes in ({'blah' : 999}, {}, None):

            attributes = {'blah' : 999}
            graph = Graph(1, 'graph', attributes)
            defaults = Defaults('node', attributes)
            node = Node(2, attributes)
            edge = Edge(3, 4, attributes)

            for obj in (graph, defaults, node, edge):
                with self.subTest(attributes=attributes, obj=obj):
                    self.assertIsNot(obj.attributes, attributes)


    def test_Defaults(self):

        self.assertRaises(ValueError, Defaults, 'key', attributes={'label': 'A label'})

        defaults = Defaults('node', attributes={'label': 'A label'})
        self.assertEqual(str(defaults), 'node [label="A label"];')
        indent = Indent(3)
        indent.indent()
        self.assertEqual(defaults.to_dot(indent), '   node [label="A label"];')

    def test_Node(self):

        node = Node('A Key', {'label' : 'A Key Label'})
        self.assertEqual(str(node), '"A Key" [label="A Key Label"];')

        node = Node('A Key')
        self.assertEqual(str(node), '"A Key";')

    def test_Edge(self):

        node1 = Node('Key One', {'label' : 'A Label'})
        node2 = Node('Key Two')

        edge = Edge(node1.key, node2.key)
        self.assertEqual(str(edge), '"Key One" -> "Key Two";')

        edge = Edge(node1.key, node2.key, {'color' : 'white'})
        self.assertEqual(str(edge), '"Key One" -> "Key Two" [color="white"];')

    def test_Rank(self):

        rank = Rank(['a', 'b', 'c d'])
        self.assertEqual(str(rank), '{rank=same "a" "b" "c d"};')

    def test_Graph(self):

        node1 = Node('Key One', {'label' : 'A Label', 'color' : 'piss yellow'})
        node2 = Node('Key Two')

        edge = Edge(node1.key, node2.key)
        self.assertEqual(str(edge), '"Key One" -> "Key Two";')

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

        self.assertEqual(graph.to_dot(), trim('''
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

