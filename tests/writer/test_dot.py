from dataclasses import dataclass, field

from snutree.model.tree import Entity, Member, Relationship, Tree, TreeConfig
from snutree.tool.dot import Edge, Id, Node
from snutree.writer.dot import (
    CustomComponentConfig,
    DotWriter,
    DotWriterConfig,
)
from tests.conftest import trim


@dataclass
class BasicDotPayload:
    dot_attributes: dict[str, Id] = field(default_factory=lambda: {"label": "test"})


def test_write_family_tree() -> None:

    tree = Tree(
        rank_type=int,
        entities={
            "100": Member(payload=BasicDotPayload(), rank=2),
            "50": Member(payload=BasicDotPayload(), rank=1),
            "a": Entity(payload=BasicDotPayload(), rank=1),
        },
        relationships={
            ("a", "50"): Relationship(payload=BasicDotPayload()),
            ("50", "100"): Relationship(payload=BasicDotPayload()),
        },
        config=TreeConfig(
            rank_min_offset=-1,
            rank_max_offset=1,
        ),
    )

    writer = DotWriter(
        DotWriterConfig(
            custom=CustomComponentConfig(
                nodes=[Node("i"), Node("ii")],
                edges=[Edge("i", "ii")],
            ),
        ),
    )

    dot = writer.write_family_tree(tree)

    expected = trim(
        """
        digraph "family-tree" {
            subgraph "ranks-left" {
                "ranks-left:0";
                "ranks-left:1";
                "ranks-left:2";
                "ranks-left:3";
                "ranks-left:0" -> "ranks-left:1";
                "ranks-left:1" -> "ranks-left:2";
                "ranks-left:2" -> "ranks-left:3";
            }
            subgraph "members" {
                "100" [label="test"];
                "50" [label="test"];
                "a" [label="test"];
                "i";
                "ii";
                "50" -> "100" [label="test"];
                "a" -> "50" [label="test"];
                "i" -> "ii";
            }
            subgraph "ranks-right" {
                "ranks-right:0";
                "ranks-right:1";
                "ranks-right:2";
                "ranks-right:3";
                "ranks-right:0" -> "ranks-right:1";
                "ranks-right:1" -> "ranks-right:2";
                "ranks-right:2" -> "ranks-right:3";
            }
            subgraph "ranks" {
                subgraph {
                    "ranks-left:0";
                    "ranks-right:0";
                }
                subgraph {
                    "ranks-left:1";
                    "ranks-right:1";
                    "50";
                    "a";
                }
                subgraph {
                    "ranks-left:2";
                    "ranks-right:2";
                    "100";
                }
                subgraph {
                    "ranks-left:3";
                    "ranks-right:3";
                }
            }
        }
        """
    )

    assert str(dot) == expected, str(dot)
