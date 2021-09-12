from dataclasses import dataclass
from typing import Iterable, Optional

from pydantic.tools import parse_obj_as

from snutree.model.member.common import BaseMember
from snutree.model.semester import Semester
from snutree.model.tree import Entity, EntityId, ParentKeyStatus


class KeyedMember(BaseMember):
    key: str
    big_key: Optional[str]
    name: str
    semester: Semester


@dataclass
class KeyedMemberParser:
    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[Entity[Semester, KeyedMember]]:
        for row in rows:
            member = parse_obj_as(KeyedMember, row)
            yield Entity(
                parent_key=EntityId(member.big_key) if member.big_key is not None else ParentKeyStatus.UNKNOWN,
                key=EntityId(member.key),
                rank=member.semester,
                member=member,
            )
