from dataclasses import dataclass

from snutree.model.tree import Member, RankedEntity, Tree, TreeConfig
from snutree.tool.dot import Edge, Node
from snutree.writer.dot import (
    DotWriter,
    DotWriterConfig,
    DynamicNodeAttributesConfig,
    EdgesConfig,
    NodesConfig,
)
from tests.conftest import trim


@dataclass
class BasicDotComponent:
    pass


@dataclass
class BasicDotMember(BasicDotComponent, Member):
    pass


def test_write_family_tree() -> None:

    tree = Tree[BasicDotComponent, None, int](
        rank_type=int,
        ranked_entities={
            "100": RankedEntity(2, BasicDotMember()),
            "50": RankedEntity(1, BasicDotMember()),
            "a": RankedEntity(1, BasicDotComponent()),
        },
        relationships={
            ("a", "50"): None,
            ("50", "100"): None,
        },
        config=TreeConfig(
            rank_min_offset=-1,
            rank_max_offset=1,
        ),
    )

    writer = DotWriter(
        DotWriterConfig[BasicDotComponent, None, int](
            edge=EdgesConfig(
                custom=[Edge("i", "ii")],
            ),
            node=NodesConfig(
                attributes=DynamicNodeAttributesConfig(
                    member=lambda _: {"label": "test"},
                ),
                custom=[Node("i"), Node("ii")],
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
                "50" -> "100";
                "a" -> "50";
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
                    rank="same";
                    "ranks-left:0";
                    "ranks-right:0";
                }
                subgraph {
                    rank="same";
                    "ranks-left:1";
                    "ranks-right:1";
                    "50";
                    "a";
                }
                subgraph {
                    rank="same";
                    "ranks-left:2";
                    "ranks-right:2";
                    "100";
                }
                subgraph {
                    rank="same";
                    "ranks-left:3";
                    "ranks-right:3";
                }
            }
        }
        """
    )

    assert str(dot) == expected, str(dot)
