from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

import pytest
from _pytest.config import Config

from snutree.api import SnutreeApi
from snutree.model.member.sigmanu.affiliation import ChapterId
from snutree.model.member.sigmanu.member import SigmaNuMember
from snutree.model.member.sigmanu.pipeline import (
    SigmaNuAssembler,
    SigmaNuParser,
)
from snutree.model.semester import Semester
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

    cycler = Cycler(deque(x11.COLORS))

    family_colors = defaultdict(
        cycler.__next__,
        {
            key: cycler.consume(value)
            for key, value in {
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
            }.items()
        },
    )

    api = SnutreeApi[SigmaNuMember, None, Semester](
        parser=SigmaNuParser(
            chapter_id=ChapterId("Delta Alpha"),
        ),
        assembler=SigmaNuAssembler(),
        writer=DotWriter(
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
                            "color": family_colors[family_id],
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
        ),
    )

    root = Path(__file__).parent
    input_path = (root / "input" / case.name).with_suffix(".csv")
    actual = api.run(input_path)
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
