from dataclasses import dataclass

from snutree.model.entity import Entity, EntityId, ParentKeyStatus
from snutree.model.tree import FamilyTree, FamilyTreeConfig
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
            Entity(EntityId("50"), EntityId("100"), 2, BasicDotMember()),
            Entity(ParentKeyStatus.NONE, EntityId("50"), 1, BasicDotMember()),
            Entity(ParentKeyStatus.NONE, EntityId("a"), 1, None),
        ],
        relationships={
            (EntityId("a"), EntityId("50")),
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
        digraph "family_tree" {
            subgraph "datesL" {
                "0L";
                "1L";
                "2L";
                "3L";
                "0L" -> "1L";
                "1L" -> "2L";
                "2L" -> "3L";
            }
            subgraph "members" {
                "100" [label="test"];
                "a";
                "50" [label="test"];
                "i";
                "ii";
                "50" -> "100";
                "a" -> "50";
                "i" -> "ii";
            }
            subgraph "datesR" {
                "0R";
                "1R";
                "2R";
                "3R";
                "0R" -> "1R";
                "1R" -> "2R";
                "2R" -> "3R";
            }
            subgraph "ranks" {
                subgraph {
                    rank="same";
                    "0L";
                    "0R";
                }
                subgraph {
                    rank="same";
                    "1L";
                    "1R";
                    "50";
                    "a";
                }
                subgraph {
                    rank="same";
                    "2L";
                    "2R";
                    "100";
                }
                subgraph {
                    rank="same";
                    "3L";
                    "3R";
                }
            }
        }
        """
    )

    assert str(dot) == expected, str(dot)
