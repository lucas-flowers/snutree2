from collections import defaultdict, deque

from snutree.api import SnutreeApi
from snutree.model.member.sigmanu.affiliation import ChapterId
from snutree.model.member.sigmanu.member import SigmaNuMember
from snutree.model.member.sigmanu.pipeline import (
    SigmaNuAssembler,
    SigmaNuParser,
)
from snutree.model.semester import Semester
from snutree.reader.csv import CsvReader
from snutree.reader.json import JsonReader
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

__snutree__ = SnutreeApi[SigmaNuMember, None, Semester](
    readers=[
        CsvReader(),
        JsonReader(),
    ],
    parser=SigmaNuParser(
        chapter_id=ChapterId("Delta Alpha"),
        require_semester=False,
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
