from dataclasses import dataclass
from typing import Callable
from unittest.mock import patch

import pytest

# from conftest import trim
from snutree.tool.dot.factory import (
    Attribute,
    Digraph,
    Edge,
    Graph,
    Node,
    StrictDigraph,
    StrictGraph,
    Subgraph,
)
from snutree.tool.dot.model import _Component, _EdgeOp, _Statement
from tests.conftest import TestCase, trim


@dataclass
class _ComponentTestCase(TestCase):
    statement: _Statement
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        _ComponentTestCase(
            id="attribute-positional-string",
            statement=Attribute("key", "value"),
            expected='key="value"',
        ),
        _ComponentTestCase(
            id="attribute-positional-html-like-str",
            statement=Attribute("key", "<value>"),
            expected="key=<value>",
        ),
        _ComponentTestCase(
            id="attribute-positional-int",
            statement=Attribute("key", 10),
            expected="key=10",
        ),
        _ComponentTestCase(
            id="attribute-positional-float",
            statement=Attribute("key", 1.5),
            expected="key=1.5",
        ),
        _ComponentTestCase(
            id="kwarg-str",
            statement=Attribute(key="value"),
            expected='key="value"',
        ),
        _ComponentTestCase(
            id="kwarg-html-like-str",
            statement=Attribute(key="<value>"),
            expected="key=<value>",
        ),
        _ComponentTestCase(
            id="kwarg-int",
            statement=Attribute(key=10),
            expected="key=10",
        ),
        _ComponentTestCase(
            id="kwarg-float",
            statement=Attribute(key=1.5),
            expected="key=1.5",
        ),
        _ComponentTestCase(
            id="node-defaults",
            statement=Node(),
            expected="node []",
        ),
        _ComponentTestCase(
            id="node-defaults",
            statement=Node(a="Test", b=5),
            expected='node [a="Test",b=5]',
        ),
        _ComponentTestCase(
            id="node",
            statement=Node("test"),
            expected='"test"',
        ),
        _ComponentTestCase(
            id="node",
            statement=Node("test", a="Test", b=5),
            expected='"test" [a="Test",b=5]',
        ),
        _ComponentTestCase(
            id="edge-defaults",
            statement=Edge(),
            expected="edge []",
        ),
        _ComponentTestCase(
            id="edge-defaults",
            statement=Edge(a="Test", b=5),
            expected='edge [a="Test",b=5]',
        ),
        _ComponentTestCase(
            id="edge",
            statement=Edge("test1", "test2"),
            expected='"test1" -> "test2"',
        ),
        _ComponentTestCase(
            id="edge",
            statement=Edge("test1", "test2", a="Test", b=5),
            expected='"test1" -> "test2" [a="Test",b=5]',
        ),
        _ComponentTestCase(
            id="edge",
            statement=Edge("test1", "test2", "test3"),
            expected='"test1" -> "test2" -> "test3"',
        ),
        _ComponentTestCase(
            id="edge",
            statement=Edge("i", "ii", "iii", a="Test", b=5),
            expected='"i" -> "ii" -> "iii" [a="Test",b=5]',
        ),
    ],
)
def test_component(case: _ComponentTestCase) -> None:
    assert str(case.statement) == case.expected


@dataclass
class ComponentAttributeKwargsTestCase(TestCase):
    construct: Callable[[], _Statement]
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        ComponentAttributeKwargsTestCase(
            id="not-enough",
            construct=Attribute,
            expected="Must provide a key and a value",
        ),
        ComponentAttributeKwargsTestCase(
            id="too-many",
            construct=lambda: Attribute(a=1, b=2),
            expected="Only a single kwarg is permitted",
        ),
    ],
)
def test_component_attribute_kwargs(case: ComponentAttributeKwargsTestCase) -> None:
    with pytest.raises(ValueError, match=case.expected):
        case.construct()


@dataclass
class _EdgeOpTestCase(TestCase):
    edge_op: _EdgeOp
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        _EdgeOpTestCase(
            id="default",
            edge_op=_Component.EDGE_OP,
            expected='"a" -> "b"',
        ),
        _EdgeOpTestCase(
            id="directed",
            edge_op=_EdgeOp.DIRECTED,
            expected='"a" -> "b"',
        ),
        _EdgeOpTestCase(
            id="undirected",
            edge_op=_EdgeOp.UNDIRECTED,
            expected='"a" -- "b"',
        ),
    ],
)
def test_edge_op(case: _EdgeOpTestCase) -> None:
    with patch.object(_Component, "EDGE_OP", new=case.edge_op):
        assert str(Edge("a", "b")) == case.expected


@dataclass
class GraphTestCase(TestCase):
    graph: _Statement
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        GraphTestCase(
            id="graph-unnamed-empty",
            graph=Graph(),
            expected=trim(
                """
                    graph {
                    }
                """
            ),
        ),
        GraphTestCase(
            id="graph-defaults",
            graph=Graph(a=1, b="2"),
            expected='graph [a=1,b="2"]',
        ),
        GraphTestCase(
            id="graph-unnamed-nonempty",
            graph=Graph(Attribute(a=1), Node(b=2)),
            expected=trim(
                """
                    graph {
                        a=1;
                        node [b=2];
                    }
                """
            ),
        ),
        GraphTestCase(
            id="graph-named-empty",
            graph=Graph("Test"),
            expected=trim(
                """
                    graph "Test" {
                    }
                """
            ),
        ),
        GraphTestCase(
            id="graph-named-nonempty",
            graph=Graph("Test", Attribute(a=1), Node(b=2)),
            expected=trim(
                """
                    graph "Test" {
                        a=1;
                        node [b=2];
                    }
                """
            ),
        ),
        GraphTestCase(
            id="graph-ignore-falsy",
            graph=Graph("Test", Node(a=1), None, Node(b=2)),
            expected=trim(
                """
                    graph "Test" {
                        node [a=1];
                        node [b=2];
                    }
                """
            ),
        ),
        GraphTestCase(
            id="strict-graph",
            graph=StrictGraph(),
            expected=trim(
                """
                    strict graph {
                    }
                """
            ),
        ),
        GraphTestCase(
            id="digraph",
            graph=Digraph(),
            expected=trim(
                """
                    digraph {
                    }
                """
            ),
        ),
        GraphTestCase(
            id="strict-digraph",
            graph=StrictDigraph(),
            expected=trim(
                """
                    strict digraph {
                    }
                """
            ),
        ),
        GraphTestCase(
            id="subgraph-unnamed-empty-no-subgraph-keyword",
            graph=Subgraph(),
            expected=trim(
                """
                    {
                    }
                """
            ),
        ),
        GraphTestCase(
            id="subgraph-unnamed-nonempty-no-subgraph-keyword",
            graph=Subgraph(Attribute(a=1), Node(b=2)),
            expected=trim(
                """
                    {
                        a=1;
                        node [b=2];
                    }
                """
            ),
        ),
        GraphTestCase(
            id="subgraph-named-empty",
            graph=Subgraph("Test"),
            expected=trim(
                """
                    subgraph "Test" {
                    }
                """
            ),
        ),
        GraphTestCase(
            id="subgraph-named-nonempty",
            graph=Subgraph("Test", Attribute(a=1), Node(b=2)),
            expected=trim(
                """
                    subgraph "Test" {
                        a=1;
                        node [b=2];
                    }
                """
            ),
        ),
    ],
)
def test_graph(case: GraphTestCase) -> None:
    assert str(case.graph) == case.expected


def test_dot() -> None:
    """
    Test a single, more complicated graph.
    """

    graph = Digraph(
        "tree",
        Attribute(size="5"),
        Attribute(width="gold"),
        Graph(rankdir="LR"),
        Node(penwidth="5", width="4"),
        Edge(penwidth="4", width="5"),
        Node("Key One", color="piss yellow", label="A Label"),
        Edge("Key One", "Key Two"),
        Node("Key Two"),
        Subgraph(
            "something",
            Edge(label="this"),
            Node("S1", label="5"),
            Node("S2"),
        ),
        Subgraph(
            Attribute(rank="same"),
            Node("Key One"),
            Node("Key Two"),
        ),
    )

    assert str(graph) == trim(
        """
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
        }
        """
    )
