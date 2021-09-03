from csv import DictReader
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest

from snutree.model.semester import Semester
from snutree.model.tree import Member, Relationship, Tree
from snutree.tool.dot import Id
from snutree.writer.dot import (
    AttributesConfig,
    DotWriter,
    DotWriterConfig,
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
    class DotMemberPayload:
        big_badge: Optional[str]
        badge: str
        label: str

        @property
        def dot_attributes(self) -> dict[str, Id]:
            return {"label": self.label}

    @dataclass
    class DotRelationshipPayload:
        @property
        def dot_attributes(self) -> dict[str, Id]:
            return {}

    members = [
        Member(
            rank=Semester(row["semester"]),
            payload=DotMemberPayload(
                big_badge=row["big_badge"] or None,
                badge=row["badge"],
                label=fr'{row["last_name"]}\n{row["badge"]}',
            ),
        )
        for row in rows
    ]

    tree = Tree(
        rank_type=Semester,
        entities={str(member.payload.badge): member for member in members},
        relationships={
            (member.payload.big_badge, member.payload.badge): Relationship(DotRelationshipPayload())
            for member in members
            if member.payload.big_badge is not None
        },
    )

    writer = DotWriter(
        DotWriterConfig(
            graph=GraphsConfig(
                defaults=AttributesConfig(
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
                defaults=AttributesConfig(
                    root=dict(
                        style="filled",
                        shape="box",
                        penwidth=2,
                        width=1.63,
                        fontname="dejavu sans",
                    ),
                    members=dict(
                        fillcolor=".11 .71 1.",
                    ),
                    ranks=dict(
                        color="none",
                        fontsize=20,
                        fontname="dejavu serif",
                    ),
                ),
            ),
            edge=EdgesConfig(
                defaults=AttributesConfig(
                    root=dict(
                        arrowhead="none",
                    ),
                    ranks=dict(
                        style="invis",
                    ),
                ),
            ),
        ),
    )

    actual = str(writer.write_family_tree(tree))
    assert actual == output_path.read_text(), actual
