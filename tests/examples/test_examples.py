from collections import deque
from csv import DictReader
from dataclasses import dataclass
from pathlib import Path

import pytest
from _pytest.config import Config
from pydantic.tools import parse_obj_as

from snutree.model.member.sigmanu.member import SigmaNuMember
from snutree.model.semester import Semester
from snutree.model.tree import RankedEntity, Tree
from snutree.tool import x11
from snutree.tool.cycler import Cycler
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
def test_examples(pytestconfig: Config, case: ExampleTestCase) -> None:

    root = Path(__file__).parent
    input_path = (root / "input" / case.name).with_suffix(".csv")

    with input_path.open() as f:
        rows = list(DictReader(f))

    members = parse_obj_as(list[SigmaNuMember], rows)

    tree = Tree[SigmaNuMember, None, Semester](
        rank_type=Semester,
        ranked_entities={
            member.key: RankedEntity(
                rank=member.semester,
                entity=member,
            )
            for member in members
        },
        relationships={
            (
                member.big_badge,
                member.key,
            ): None
            for member in members
            if member.big_badge is not None
        },
    )

    @dataclass
    class ColorCycler:

        family_colors: dict[str, str]
        cycler: Cycler[str]

        def __post_init__(self) -> None:
            for color in self.family_colors.values():
                self.cycler.consume(color)

        def get(self, family_id: str) -> str:
            if family_id not in self.family_colors:
                self.family_colors[family_id] = next(self.cycler)
            return self.family_colors[family_id]

    cycler = ColorCycler(
        {
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
        },
        Cycler(deque(x11.COLORS)),
    )

    writer = DotWriter[SigmaNuMember, None, Semester](
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
                    member=lambda member: {
                        "label": r"\n".join([member.name, member.affiliation]),
                    },
                    rank=lambda rank: {
                        "label": str(rank),
                    },
                    family=lambda family_id: {
                        "color": cycler.get(family_id),
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
    expected_path = (root / "output" / case.name).with_suffix(".dot")

    # Do not directly assert equality, to avoid generating pytest comparison
    # output, which is really slow for the large files used in these test cases
    if not expected_path.exists() or actual != expected_path.read_text():
        overwrite: bool = pytestconfig.getoption("--overwrite")
        if overwrite:
            expected_path.write_text(actual)
            pytest.fail("output changed; overwrote sample file")
        else:
            pytest.fail("output changed")
