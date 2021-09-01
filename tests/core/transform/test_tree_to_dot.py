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
from snutree.tool.dot import Edge, Node
from tests.conftest import trim


def test_create_family_tree() -> None:

    tree = Tree[int](
        rank_type=int,
        entities={
            "100": Member([], {}, rank=2),
            "50": Member([], {}, rank=1),
            "a": Entity([], {}, rank=1),
        },
        relationships={
            ("a", "50"): Relationship([], {}),
            ("50", "100"): Relationship([], {}),
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
                "100";
                "50";
                "a";
                "i";
                "ii";
                "50" -> "100";
                "a" -> "50";
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
