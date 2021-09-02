from dataclasses import dataclass, field

from snutree.core.model.tree import (
    Entity,
    Member,
    Relationship,
    Tree,
    TreeConfig,
)
from snutree.core.transform.tree_to_dot import (
    Config,
    CustomConfig,
    create_family_tree,
)
from snutree.tool.dot import Edge, Id, Node
from tests.conftest import trim


@dataclass
class BasicDotPayload:
    dot_attributes: dict[str, Id] = field(default_factory=lambda: {"label": "test"})


def test_create_family_tree() -> None:

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
            rank_min_offset=0,
            rank_max_offset=0,
        ),
    )

    dot = create_family_tree(
        tree=tree,
        config=Config(
            custom=CustomConfig(
                nodes=[Node("i"), Node("ii")],
                edges=[Edge("i", "ii")],
            ),
        ),
    )

    expected = trim(
        """
        digraph "family-tree" {
            subgraph "ranks-left" {
                "ranks-left:1";
                "ranks-left:2";
                "ranks-left:1" -> "ranks-left:2";
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
                "ranks-right:1";
                "ranks-right:2";
                "ranks-right:1" -> "ranks-right:2";
            }
            subgraph "ranks" {
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
            }
        }
        """
    )

    assert str(dot) == expected, str(dot)
