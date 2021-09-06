from dataclasses import dataclass
from typing import Iterable, Optional

from pydantic.tools import parse_obj_as

from snutree.model.member.common import BaseMember
from snutree.model.semester import Semester
from snutree.model.tree import FamilyTree, FamilyTreeConfig, RankedEntity


class KeyedMember(BaseMember):
    key: str
    big_key: Optional[str]
    name: str
    semester: Semester


@dataclass
class KeyedMemberParser:
    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[KeyedMember]:
        for row in rows:
            yield parse_obj_as(KeyedMember, row)


@dataclass
class KeyedMemberAssembler:
    def assemble(
        self, tree_config: FamilyTreeConfig, members: Iterable[KeyedMember]
    ) -> FamilyTree[KeyedMember, None, Semester]:
        ranked_entities: dict[str, RankedEntity[Semester, KeyedMember]] = {}
        relationships: dict[tuple[str, str], None] = {}
        for member in members:
            ranked_entities[member.key] = RankedEntity(member.semester, member)
            if member.big_key is not None:
                relationships[(member.big_key, member.key)] = None
        return FamilyTree(Semester, ranked_entities, relationships, tree_config)
