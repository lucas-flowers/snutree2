from dataclasses import dataclass
from typing import Iterable

from pydantic.tools import parse_obj_as

from snutree.model.member.sigmanu.affiliation import ChapterId
from snutree.model.member.sigmanu.member import (
    Brother,
    Candidate,
    SigmaNuMember,
)
from snutree.model.semester import Semester
from snutree.model.tree import Entity


@dataclass
class SigmaNuParser:

    chapter_id: ChapterId
    require_semester: bool
    last_candidate_key: int = 0
    last_brother_key: int = 0

    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[Entity[Semester, SigmaNuMember]]:

        for row in rows:
            obj: dict[str, object] = {"chapter": self.chapter_id, **row}
            if self.require_semester or obj.get("semester"):

                member: SigmaNuMember = parse_obj_as(SigmaNuMember, obj)  # type: ignore[arg-type]

                if isinstance(member, Candidate):
                    self.last_candidate_key += 1
                    key = f"candidate{self.last_candidate_key}"
                elif isinstance(member, Brother):
                    self.last_brother_key += 1
                    key = f"brother{self.last_brother_key}"
                else:
                    key = member.badge

                yield Entity(member.big_badge, key, member.semester, member)
