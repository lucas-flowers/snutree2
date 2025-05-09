from collections.abc import Iterable
from dataclasses import dataclass, field

from pydantic import TypeAdapter

from snutree.model.entity import Entity, EntityId, ParentKeyStatus
from snutree.model.member.sigmanu.affiliation import ChapterId
from snutree.model.member.sigmanu.member import (
    Brother,
    Candidate,
    SigmaNuMember,
)
from snutree.model.semester import Semester


@dataclass
class SigmaNuParser:
    default_chapter_id: ChapterId | None
    require_semester: bool
    last_candidate_key: int = -1
    last_brother_key: int = -1
    root_member_badges: set[str] = field(default_factory=set)

    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[Entity[Semester, SigmaNuMember]]:
        default_chapter_column = {"chapter": self.default_chapter_id} if self.default_chapter_id is not None else {}

        for row in rows:
            obj: dict[str, object] = {
                key: value or None
                for key, value in {
                    **default_chapter_column,
                    **row,
                }.items()
            }
            if self.require_semester or obj.get("semester"):
                member: SigmaNuMember = TypeAdapter(SigmaNuMember).validate_python(obj)

                if isinstance(member, Candidate):
                    self.last_candidate_key += 1
                    key = EntityId(f"Candidate {self.last_candidate_key}")
                elif isinstance(member, Brother):
                    self.last_brother_key += 1
                    key = EntityId(f"Brother {self.last_brother_key}")
                else:
                    key = EntityId(str(member.badge))

                parent_key: EntityId | ParentKeyStatus
                if member.big_badge is not None:
                    parent_key = EntityId(str(member.big_badge))
                elif key in self.root_member_badges:
                    parent_key = ParentKeyStatus.NONE
                else:
                    parent_key = ParentKeyStatus.UNKNOWN

                yield Entity(parent_key, key, member.semester, member)
