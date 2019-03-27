
from unittest.mock import patch

import pytest

from conftest import trim
from snutree.model.dot import (
    abstract,
    Attribute,
    Node,
    Edge,
    Graph,
    StrictGraph,
    Digraph,
    StrictDigraph,
    Subgraph,
)

@pytest.mark.parametrize('construct, expected', [

    ## ATTRIBUTES

    # Attribute(key, value): Positional argument style
    (lambda: Attribute('key', 'value'), 'key="value"'), # Strings
    (lambda: Attribute('key', '<value>'), 'key=<value>'), # HTML-like strings
    (lambda: Attribute('key', 10), 'key=10'), # Integers
    (lambda: Attribute('key', 1.5), 'key=1.5'), # Floats

    # Attribute(key=value): Keyword argument style
    (lambda: Attribute(key='value'), 'key="value"'), # Strings
    (lambda: Attribute(key='<value>'), 'key=<value>'), # HTML-like strings
    (lambda: Attribute(key=10), 'key=10'), # Integers
    (lambda: Attribute(key=1.5), 'key=1.5'), # Floats

    # Wrong number of attributes
    (lambda: Attribute(), TypeError),
    (lambda: Attribute('key'), TypeError),
    (lambda: Attribute('key', 'value1', 'value2'), TypeError),
    (lambda: Attribute('key1', 'value1', key2='value2'), TypeError),
    (lambda: Attribute(key1='value1', key2='value2'), TypeError),

    ## NODES

    # Node(**attributes): Node defaults
    (lambda: Node(), 'node []'),
    (lambda: Node(a='Test', b=5), 'node [a="Test",b=5]'),

    # Node(identifier, **attributes): Node
    (lambda: Node('test'), '"test"'),
    (lambda: Node('test', a='Test', b=5), '"test" [a="Test",b=5]'),

    # Too many identifiers
    (lambda: Node('key1', 'key2'), TypeError),
    (lambda: Node('key1', 'key2', label='Test'), TypeError),

    ## EDGES

    # Edge(**attributes): Edge defaults
    (lambda: Edge(), 'edge []'),
    (lambda: Edge(a='Test', b=5), 'edge [a="Test",b=5]'), # Defaults

    # Edge cannot have one Node
    (lambda: Edge('key1'), TypeError),
    (lambda: Edge('key1', label='Test'), TypeError),

    # Edge(*identifiers, **attributes)
    (lambda: Edge('test1', 'test2'), '"test1" -> "test2"'),
    (lambda: Edge('test1', 'test2', a='Test', b=5), '"test1" -> "test2" [a="Test",b=5]'),
    (lambda: Edge('test1', 'test2', 'test3'), '"test1" -> "test2" -> "test3"'),
    (lambda: Edge('test1', 'test2', 'test3', a='Test', b=5), '"test1" -> "test2" -> "test3" [a="Test",b=5]'),

])
def test_component(construct, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            construct()
    else:
        statement = construct()
        assert str(statement) == expected
        assert statement.to_blocks() == [f'{expected};']

@pytest.mark.parametrize('edge_op, expected', [
    (abstract.Component.EDGE_OP, '"a" -> "b"'),
    (abstract.EdgeOp.DIRECTED, '"a" -> "b"'),
    (abstract.EdgeOp.UNDIRECTED, '"a" -- "b"'),
])
def test_EDGE_OP(edge_op, expected):
    with patch.object(abstract.Component, 'EDGE_OP', new=edge_op):
        assert str(Edge('a', 'b')) == expected

@pytest.mark.parametrize('construct, expected', [

    ## GRAPH

    # Graph(): Unnamed and empty
    (
        lambda: Graph(),
        trim('''
            graph {
            }
        ''')
    ),

    # Graph(**attributes): Graph defaults
    (
        lambda: Graph(a=1, b='2'),
        'graph [a=1,b="2"]',
    ),

    # Graph(*statements): Unnamed and nonempty
    (
        lambda: Graph(Attribute(a=1), Node(b=2)),
        trim('''
            graph {
                a=1;
                node [b=2];
            }
        '''),
    ),

    # Graph(identifier): Named and empty
    (
        lambda: Graph('Test'),
        trim('''
            graph "Test" {
            }
        '''),
    ),

    # Graph(identifier, *statements): Named and nonempty
    (
        lambda: Graph('Test', Attribute(a=1), Node(b=2)),
        trim('''
            graph "Test" {
                a=1;
                node [b=2];
            }
        '''),
    ),

    # Graph(identifier, *statements): Ignore falsy statements
    (
        lambda: Graph('Test', Node(a=1), None, False, '', Node(b=2)),
        trim('''
            graph "Test" {
                node [a=1];
                node [b=2];
            }
        '''),
    ),


    # Cannot combine normal graph mode and graph defaults mode
    (
        lambda: Graph('Test', a=1, b=2),
        TypeError,
    ),

    ## STRICT GRAPH

    (
        lambda: StrictGraph(),
        trim('''
            strict graph {
            }
        '''),
    ),

    ## DIGRAPH

    (
        lambda: Digraph(),
        trim('''
            digraph {
            }
        '''),
    ),

    ## STRICT DIGRAPH

    (
        lambda: StrictDigraph(),
        trim('''
            strict digraph {
            }
        '''),
    ),

    ## SUBGRAPH

    # Subgraph(): Unnamed and empty (no 'subgraph' keyword when unnamed)
    (
        lambda: Subgraph(),
        trim('''
            {
            }
        '''),
    ),

    # Subgraph(*statements): Unnamed and nonempty
    (
        lambda: Subgraph(Attribute(a=1), Node(b=2)),
        trim('''
            {
                a=1;
                node [b=2];
            }
        '''),
    ),

    # Subgraph(identifier): Named and empty
    (
        lambda: Subgraph('Test'),
        trim('''
            subgraph "Test" {
            }
        '''),
    ),

    # Subgraph(identifier, *statements): Named and nonempty
    (
        lambda: Subgraph('Test', Attribute(a=1), Node(b=2)),
        trim('''
            subgraph "Test" {
                a=1;
                node [b=2];
            }
        '''),
    ),

])
def test_graph(construct, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            construct()
    else:
        statement = construct()
        assert str(statement) == expected

def test_dot():
    '''
    Test a single, more complicated graph.
    '''

    graph = Digraph(
        'tree',
        Attribute(size='5'),
        Attribute(width='gold'),
        Graph(rankdir='LR'),
        Node(penwidth='5', width='4'),
        Edge(penwidth='4', width='5'),
        Node('Key One', color='piss yellow', label='A Label'),
        Edge('Key One', 'Key Two'),
        Node('Key Two'),
        Subgraph(
            'something',
            Edge(label='this'),
            Node('S1', label='5'),
            Node('S2'),
        ),
        Subgraph(
            Attribute(rank='same'),
            Node('Key One'),
            Node('Key Two'),
        ),
    )

    assert str(graph) == trim('''
        digraph "tree" {
            size="5";
            width="gold";
            graph [rankdir="LR"];
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
            {
                rank="same";
                "Key One";
                "Key Two";
            }
        }''')

