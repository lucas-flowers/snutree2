from dataclasses import dataclass

from snutree.model.tree import Entity, FamilyTree, FamilyTreeConfig
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
class BasicDotMember:
    pass


def test_write_family_tree() -> None:

    tree = FamilyTree[int, BasicDotMember](
        rank_type=int,
        entities=[
            Entity("50", "100", 2, BasicDotMember()),
            Entity(None, "50", 1, BasicDotMember()),
            Entity(None, "a", 1, None),
        ],
        relationships={
            ("a", "50"),
        },
        config=FamilyTreeConfig(
            rank_min_offset=-1,
            rank_max_offset=1,
        ),
    )

    writer = DotWriter(
        DotWriterConfig[int, BasicDotMember](
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
            subgraph "entities" {
                "100" [label="test"];
                "50" [label="test"];
                "a";
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
