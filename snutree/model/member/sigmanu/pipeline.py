from dataclasses import dataclass
from typing import Iterable

from pydantic.tools import parse_obj_as

from snutree.model.member.sigmanu.affiliation import ChapterId
from snutree.model.member.sigmanu.member import SigmaNuMember
from snutree.model.semester import Semester
from snutree.model.tree import FamilyTree, FamilyTreeConfig, RankedEntity


@dataclass
class SigmaNuParser:

    chapter_id: ChapterId
    require_semester: bool

    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[SigmaNuMember]:
        for row in rows:
            obj: dict[str, object] = {"chapter": self.chapter_id, **row}
            if self.require_semester or obj.get("semester"):
                yield parse_obj_as(SigmaNuMember, obj)  # type: ignore[arg-type]
            else:
                continue


@dataclass
class SigmaNuAssembler:
    def assemble(
        self, tree_config: FamilyTreeConfig, members: Iterable[SigmaNuMember]
    ) -> FamilyTree[SigmaNuMember, None, Semester]:
        ranked_entities: dict[str, RankedEntity[Semester, SigmaNuMember]] = {}
        relationships: dict[tuple[str, str], None] = {}
        for member in members:
            ranked_entities[member.key] = RankedEntity(member.semester, member)
            if member.big_badge is not None:
                relationships[(member.big_badge, member.key)] = None
        return FamilyTree(Semester, ranked_entities, relationships, tree_config)
