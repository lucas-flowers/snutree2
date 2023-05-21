from collections import defaultdict, deque

from snutree.api import SnutreeConfig
from snutree.model.entity import CustomEntity, ParentKeyStatus
from snutree.model.member.sigmanu.affiliation import ChapterId
from snutree.model.member.sigmanu.member import SigmaNuMember
from snutree.model.member.sigmanu.pipeline import SigmaNuParser
from snutree.model.semester import Semester
from snutree.model.tree import FamilyTreeConfig
from snutree.tool import x11
from snutree.tool.cycler import Cycler
from snutree.writer.dot import (
    DefaultAttributesConfig,
    DefaultEdgeAttributesConfig,
    DefaultNodeAttributesConfig,
    DotWriterConfig,
    DynamicEdgeAttributesConfig,
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

__snutree__ = SnutreeConfig[Semester, SigmaNuMember](
    rank_type=Semester,
    parser=SigmaNuParser(
        default_chapter_id=ChapterId("Delta Alpha"),
        require_semester=False,
        root_member_badges={
            # ΔΑ was knighted but, due to COVID-19, never received a big brother
            "1498",
            # Refounders
            "1031",
            "1034",
            "1035",
            "1036",
            "1038",
            "1039",
            "1041",
            "1043",
            "1044",
            "1045",
            "1046",
            "1047",
            "1048",
            "1049",
            "1050",
            "1051",
        },
    ),
    custom_entities=[
        CustomEntity(
            parent_key=ParentKeyStatus.NONE,
            key="Reorganization",
            rank=Semester("Spring 1989"),
        ),
        # The home chapter of ΔA 986, who transferred to CWRU from Duquesne
        CustomEntity(
            parent_key=ParentKeyStatus.NONE,
            key="Kappa Delta",
            rank=Semester("Fall 1982"),
        ),
    ],
    custom_relationships={
        # Connect ΔA 986 to his home chapter
        ("Kappa Delta", "986"),
        # Connect refounders from the old chapter to Reorganization
        ("Reorganization", "1031"),
        ("Reorganization", "1034"),
        ("Reorganization", "1035"),
        ("Reorganization", "1036"),
        ("Reorganization", "1038"),
        ("Reorganization", "1039"),
        ("Reorganization", "1041"),
        # Make Reorganization the "big" of the new refounders
        ("Reorganization", "1043"),
        ("Reorganization", "1044"),
        ("Reorganization", "1045"),
        ("Reorganization", "1046"),
        ("Reorganization", "1047"),
        ("Reorganization", "1048"),
        ("Reorganization", "1049"),
        ("Reorganization", "1050"),
        ("Reorganization", "1051"),
    },
    tree=FamilyTreeConfig(
        seed=4445,
        include_unknowns=True,
        include_singletons=True,
        include_families=None,
        rank_min=Semester("Spring 1950"),  # Spring 1950 is right before the start of the earliest non-singleton family
        rank_max=None,
        rank_max_offset=1,
    ),
    writer=DotWriterConfig(
        draw_ranks=True,
        graph=GraphsConfig(
            defaults=DefaultAttributesConfig(
                root=dict(
                    size="80",
                    ratio="compress",
                    pad=".5, .5",
                    ranksep=".25",
                    nodesep=".3",
                    label="Family Tree: Delta Alpha Chapter of Sigma Nu Fraternity",
                    labelloc="t",
                    fontsize="110",
                    concentrate=False,
                    mclimit=64,
                    splines="polyline",
                ),
            ),
        ),
        node=NodesConfig(
            defaults=DefaultNodeAttributesConfig(
                root=dict(
                    style="filled",
                    shape="box",
                    penwidth=2,
                    height="0.5",
                    width="0",
                    fontname="dejavu sans",
                    margin=".04,.02",
                ),
                entity=dict(
                    fillcolor=".11 .71 1.",
                ),
                unknown=dict(
                    height="0",
                    width="0",
                    style="invis",
                ),
                singleton=dict(
                    penwidth=0,
                    width=0,
                    style="",
                ),
                rank=dict(
                    color="none",
                    fontsize="20",
                    fontname="dejavu serif",
                    height="0.55",  # Make a little taller than other nodes to allow space for edges
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
                by_key={
                    "Reorganization": dict(
                        height="0.6",
                        label="Reorganization",
                        shape="oval",
                    ),
                    "Kappa Delta": dict(
                        label=r"Kappa Delta Chapter\nDuquesne University",
                        color="none",
                        fillcolor="none",
                    ),
                },
            ),
        ),
        edge=EdgesConfig(
            defaults=DefaultEdgeAttributesConfig(
                root=dict(
                    arrowhead="none",
                ),
                unknown=dict(
                    style="dotted",
                ),
                rank=dict(
                    style="invis",
                ),
            ),
            attributes=DynamicEdgeAttributesConfig(
                by_key={
                    ("Reorganization", "1031"): dict(style="dashed"),
                    ("Reorganization", "1034"): dict(style="dashed"),
                    ("Reorganization", "1035"): dict(style="dashed"),
                    ("Reorganization", "1036"): dict(style="dashed"),
                    ("Reorganization", "1038"): dict(style="dashed"),
                    ("Reorganization", "1039"): dict(style="dashed"),
                    ("Reorganization", "1041"): dict(style="dashed"),
                }
            ),
        ),
    ),
)
