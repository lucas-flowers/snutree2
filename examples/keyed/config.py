from snutree.api import SnutreeConfig
from snutree.model.member.keyed import KeyedMember, KeyedMemberParser
from snutree.model.semester import Semester
from snutree.model.tree import FamilyTreeConfig
from snutree.writer.dot import (
    DefaultAttributesConfig,
    DefaultEdgeAttributesConfig,
    DefaultNodeAttributesConfig,
    DotWriter,
    DotWriterConfig,
    DynamicNodeAttributesConfig,
    EdgesConfig,
    GraphsConfig,
    NodesConfig,
)

__snutree__ = SnutreeConfig[Semester, KeyedMember](
    rank_type=Semester,
    parser=KeyedMemberParser(),
    tree=FamilyTreeConfig(
        seed=23,
    ),
    writers={
        "dot": DotWriter(
            DotWriterConfig(
                draw_ranks=False,
                graph=GraphsConfig(
                    defaults=DefaultAttributesConfig(
                        root=dict(
                            label="Example",
                            rankdir="LR",
                            ratio="compress",
                        ),
                    ),
                ),
                node=NodesConfig(
                    defaults=DefaultNodeAttributesConfig(
                        root=dict(
                            shape="box",
                        ),
                        unknown=dict(
                            style="invis",
                        ),
                    ),
                    attributes=DynamicNodeAttributesConfig(
                        member=lambda member: {"label": member.name},
                    ),
                ),
                edge=EdgesConfig(
                    defaults=DefaultEdgeAttributesConfig(
                        root=dict(
                            arrowhead="none",
                        ),
                    ),
                ),
            ),
        ),
    },
)
