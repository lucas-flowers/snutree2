from dataclasses import dataclass
from typing import Iterable

from pydantic.tools import parse_obj_as

from snutree.model.member.sigmanu.affiliation import ChapterId
from snutree.model.member.sigmanu.member import SigmaNuMember
from snutree.model.semester import Semester
from snutree.model.tree import FamilyTree, RankedEntity


@dataclass
class SigmaNuParser:

    chapter_id: ChapterId

    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[SigmaNuMember]:
        for row in rows:
            obj: dict[str, object] = {"chapter": self.chapter_id, **row}
            yield parse_obj_as(SigmaNuMember, obj)  # type: ignore[arg-type]


@dataclass
class SigmaNuAssembler:
    def assemble(self, members: Iterable[SigmaNuMember]) -> FamilyTree[SigmaNuMember, None, Semester]:
        ranked_entities: dict[str, RankedEntity[Semester, SigmaNuMember]] = {}
        relationships: dict[tuple[str, str], None] = {}
        for member in members:
            ranked_entities[member.key] = RankedEntity(member.semester, member)
            if member.big_badge is not None:
                relationships[(member.big_badge, member.key)] = None
        return FamilyTree(Semester, ranked_entities, relationships)
