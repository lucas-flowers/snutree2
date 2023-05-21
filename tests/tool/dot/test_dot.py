from collections.abc import Callable
from dataclasses import dataclass
from unittest.mock import patch

import pytest

from snutree.tool.dot import (
    Attribute,
    Component,
    Digraph,
    Edge,
    EdgeOp,
    Graph,
    Node,
    Statement,
    StrictDigraph,
    StrictGraph,
    Subgraph,
)
from tests.conftest import TestCase, trim


@dataclass
class StatementTestCase(TestCase):
    statement: Statement
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        StatementTestCase(
            id="attribute-positional-string",
            statement=Attribute("key", "value"),
            expected='key="value"',
        ),
        StatementTestCase(
            id="attribute-positional-html-like-str",
            statement=Attribute("key", "<value>"),
            expected="key=<value>",
        ),
        StatementTestCase(
            id="attribute-positional-int",
            statement=Attribute("key", 10),
            expected="key=10",
        ),
        StatementTestCase(
            id="attribute-positional-float",
            statement=Attribute("key", 1.5),
            expected="key=1.5",
        ),
        StatementTestCase(
            id="kwarg-str",
            statement=Attribute(key="value"),
            expected='key="value"',
        ),
        StatementTestCase(
            id="kwarg-html-like-str",
            statement=Attribute(key="<value>"),
            expected="key=<value>",
        ),
        StatementTestCase(
            id="kwarg-int",
            statement=Attribute(key=10),
            expected="key=10",
        ),
        StatementTestCase(
            id="kwarg-float",
            statement=Attribute(key=1.5),
            expected="key=1.5",
        ),
        StatementTestCase(
            id="node-defaults",
            statement=Node(),
            expected="node []",
        ),
        StatementTestCase(
            id="node-defaults",
            statement=Node(a="Test", b=5),
            expected='node [a="Test",b=5]',
        ),
        StatementTestCase(
            id="node",
            statement=Node("test"),
            expected='"test"',
        ),
        StatementTestCase(
            id="node",
            statement=Node("test", a="Test", b=5),
            expected='"test" [a="Test",b=5]',
        ),
        StatementTestCase(
            id="edge-defaults",
            statement=Edge(),
            expected="edge []",
        ),
        StatementTestCase(
            id="edge-defaults",
            statement=Edge(a="Test", b=5),
            expected='edge [a="Test",b=5]',
        ),
        StatementTestCase(
            id="edge",
            statement=Edge("test1", "test2"),
            expected='"test1" -> "test2"',
        ),
        StatementTestCase(
            id="edge",
            statement=Edge("test1", "test2", a="Test", b=5),
            expected='"test1" -> "test2" [a="Test",b=5]',
        ),
        StatementTestCase(
            id="edge",
            statement=Edge("test1", "test2", "test3"),
            expected='"test1" -> "test2" -> "test3"',
        ),
        StatementTestCase(
            id="edge",
            statement=Edge("i", "ii", "iii", a="Test", b=5),
            expected='"i" -> "ii" -> "iii" [a="Test",b=5]',
        ),
        StatementTestCase(
            id="graph-unnamed-empty",
            statement=Graph(),
            expected=trim(
                """
                    graph {
                    }
                """
            ),
        ),
        StatementTestCase(
            id="graph-unnamed-nonempty",
            statement=Graph(Attribute(a=1), Node(b=2)),
            expected=trim(
                """
                    graph {
                        a=1;
                        node [b=2];
                    }
                """
            ),
        ),
        StatementTestCase(
            id="graph-named-empty",
            statement=Graph("Test"),
            expected=trim(
                """
                    graph "Test" {
                    }
                """
            ),
        ),
        StatementTestCase(
            id="graph-named-nonempty",
            statement=Graph("Test", Attribute(a=1), Node(b=2)),
            expected=trim(
                """
                    graph "Test" {
                        a=1;
                        node [b=2];
                    }
                """
            ),
        ),
        StatementTestCase(
            id="graph-ignore-falsy",
            statement=Graph("Test", Node(a=1), None, Node(b=2)),
            expected=trim(
                """
                    graph "Test" {
                        node [a=1];
                        node [b=2];
                    }
                """
            ),
        ),
        StatementTestCase(
            id="strict-graph",
            statement=StrictGraph(),
            expected=trim(
                """
                    strict graph {
                    }
                """
            ),
        ),
        StatementTestCase(
            id="digraph",
            statement=Digraph(),
            expected=trim(
                """
                    digraph {
                    }
                """
            ),
        ),
        StatementTestCase(
            id="strict-digraph",
            statement=StrictDigraph(),
            expected=trim(
                """
                    strict digraph {
                    }
                """
            ),
        ),
        StatementTestCase(
            id="subgraph-empty",
            statement=Subgraph("Test"),
            expected=trim(
                """
                    subgraph "Test" {
                    }
                """
            ),
        ),
        StatementTestCase(
            id="subgraph-nonempty",
            statement=Subgraph("Test", Attribute(a=1), Node(b=2)),
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
def test_statement(case: StatementTestCase) -> None:
    assert str(case.statement) == case.expected


@dataclass
class StatementValueErrorTestCase(TestCase):
    construct: Callable[[], Statement]
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        StatementValueErrorTestCase(
            id="not-enough",
            construct=Attribute,
            expected="Must provide a key and a value",
        ),
        StatementValueErrorTestCase(
            id="too-many",
            construct=lambda: Attribute(a=1, b=2),
            expected="Only a single kwarg is permitted",
        ),
    ],
)
def test_statement_value_error(case: StatementValueErrorTestCase) -> None:
    with pytest.raises(ValueError, match=case.expected):
        case.construct()


@dataclass
class EdgeOpTestCase(TestCase):
    edge_op: EdgeOp
    expected: str


@pytest.mark.parametrize(
    "case",
    [
        EdgeOpTestCase(
            id="default",
            edge_op=Component.EDGE_OP,
            expected='"a" -> "b"',
        ),
        EdgeOpTestCase(
            id="directed",
            edge_op=EdgeOp.DIRECTED,
            expected='"a" -> "b"',
        ),
        EdgeOpTestCase(
            id="undirected",
            edge_op=EdgeOp.UNDIRECTED,
            expected='"a" -- "b"',
        ),
    ],
)
def test_edge_op(case: EdgeOpTestCase) -> None:
    with patch.object(Component, "EDGE_OP", new=case.edge_op):
        assert str(Edge("a", "b")) == case.expected


def test_dot() -> None:
    """
    Test a single, more complicated graph.
    """

    graph = Digraph(
        "tree",
        Attribute(size="5"),
        Attribute(width="gold"),
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
            subgraph {
                rank="same";
                "Key One";
                "Key Two";
            }
        }
        """
    )
