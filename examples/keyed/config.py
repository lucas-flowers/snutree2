from snutree.api import SnutreeApi
from snutree.model.member.keyed import KeyedMember, KeyedMemberParser
from snutree.model.semester import Semester
from snutree.model.tree import FamilyTreeConfig
from snutree.reader.json import JsonReader
from snutree.writer.dot import (
    DefaultAttributesConfig,
    DotWriter,
    DotWriterConfig,
    DynamicNodeAttributesConfig,
    EdgesConfig,
    GraphsConfig,
    NodesConfig,
)

__snutree__ = SnutreeApi[Semester, KeyedMember](
    rank_type=Semester,
    readers=[
        JsonReader(),
    ],
    parser=KeyedMemberParser(),
    tree_config=FamilyTreeConfig(
        seed="23",
    ),
    writer=DotWriter(
        config=DotWriterConfig(
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
                defaults=DefaultAttributesConfig(
                    root=dict(
                        shape="box",
                    ),
                ),
                attributes=DynamicNodeAttributesConfig(
                    member=lambda member: {"label": member.name},
                ),
            ),
            edge=EdgesConfig(
                defaults=DefaultAttributesConfig(
                    root=dict(
                        arrowhead="none",
                    ),
                ),
            ),
        ),
    ),
)
