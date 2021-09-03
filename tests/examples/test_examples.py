from csv import DictReader
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

import pytest

from snutree.model.semester import Semester
from snutree.model.tree import Member, RankedEntity, Tree
from snutree.writer.dot import (
    DefaultAttributesConfig,
    DotWriter,
    DotWriterConfig,
    DynamicNodeAttributesConfig,
    EdgesConfig,
    GraphsConfig,
    NodesConfig,
)
from tests.conftest import TestCase


@dataclass
class ExampleTestCase(TestCase):
    @property
    def name(self) -> str:
        return self.id


@pytest.mark.parametrize(
    "case",
    [
        ExampleTestCase("sigmanu_basic"),
    ],
)
def test_examples(case: ExampleTestCase) -> None:

    root = Path(__file__).parent
    input_path = (root / "input" / case.name).with_suffix(".csv")
    output_path = (root / "output" / case.name).with_suffix(".dot")

    with input_path.open() as f:
        rows = list(DictReader(f))

    @dataclass
    class DotMember(Member):
        big_badge: Optional[str]
        badge: str
        label: str

    ranked_entities = [
        (
            Semester(row["semester"]),
            DotMember(
                big_badge=row["big_badge"] or None,
                badge=row["badge"],
                label=fr'{row["last_name"]}\n{row["badge"]}',
            ),
        )
        for row in rows
    ]

    tree = Tree[DotMember, None, Semester](
        rank_type=Semester,
        ranked_entities={entity.badge: RankedEntity(rank, entity) for rank, entity in ranked_entities},
        relationships={
            (entity.big_badge, entity.badge): None for rank, entity in ranked_entities if entity.big_badge is not None
        },
    )

    writer = DotWriter[DotMember, None, Semester](
        DotWriterConfig(
            graph=GraphsConfig(
                defaults=DefaultAttributesConfig(
                    root=dict(
                        size=80,
                        ratio="compress",
                        pad=".5, .5",
                        ranksep=0.15,
                        nodesep=0.5,
                        label="Family Tree: Delta Alpha Chapter of Sigma Nu Fraternity",
                        labelloc="t",
                        fontsize=110,
                        concentrate=False,
                    ),
                ),
            ),
            node=NodesConfig(
                defaults=DefaultAttributesConfig(
                    root=dict(
                        style="filled",
                        shape="box",
                        penwidth=2,
                        width=1.63,
                        fontname="dejavu sans",
                    ),
                    member=dict(
                        fillcolor=".11 .71 1.",
                    ),
                    rank=dict(
                        color="none",
                        fontsize=20,
                        fontname="dejavu serif",
                    ),
                ),
                attributes=DynamicNodeAttributesConfig(
                    member=lambda member: {"label": member.label},
                    rank=lambda rank: {"label": str(rank)},
                    family=lambda family_id: {
                        "color": {
                            "663": "deeppink",
                            "760": "brown1",
                            "722": "red4",
                            "726": "lightsteelblue",
                            "673": "midnightblue",
                            "716": "purple",
                            "702": "indianred4",
                            "735": "limegreen",
                            "757": "darkgreen",
                            "740": "royalblue4",
                            "986": "yellow",
                            "1043": "slategrey",
                            "1044": "orangered4",
                            "1045": "crimson",  # Dea family
                            "1046": "chartreuse4",
                            "1047": "cyan2",
                            "1048": "sienna2",
                            "1049": "salmon2",
                            "1050": "cadetblue",
                            "1051": "dodgerblue",  # Ochi family
                        }.get(family_id, "black"),
                    },
                ),
            ),
            edge=EdgesConfig(
                defaults=DefaultAttributesConfig(
                    root=dict(
                        arrowhead="none",
                    ),
                    rank=dict(
                        style="invis",
                    ),
                ),
            ),
        ),
    )

    actual = str(writer.write_family_tree(tree))
    try:
        assert actual == output_path.read_text()
    except AssertionError:
        with NamedTemporaryFile(delete=False) as tmpfile:
            path = Path(tmpfile.name)
            path.write_text(actual)
        pytest.fail(f"Wrote actual result to {path}")
