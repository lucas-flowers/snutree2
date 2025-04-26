from dataclasses import dataclass
from enum import Enum, auto
from operator import index
from typing import Generic, Self, TypeVar

from snutree.model.rank import AnyRank

MemberT = TypeVar("MemberT")


class ParentKeyStatus(Enum):
    UNKNOWN = auto()
    NONE = auto()


class EntityId(str):
    def __new__(cls: type[Self], value: str) -> Self:
        return super().__new__(cls, value)


@dataclass
class Entity(Generic[AnyRank, MemberT]):
    parent_key: EntityId | ParentKeyStatus
    key: EntityId
    rank: AnyRank
    member: MemberT | None


class CustomEntity(Entity[AnyRank, MemberT]):
    def __init__(self, parent_key: str | ParentKeyStatus, key: str, rank: AnyRank) -> None:
        super().__init__(
            parent_key=EntityId(parent_key) if isinstance(parent_key, str) else parent_key,
            key=EntityId(key),
            rank=rank,
            member=None,
        )


class UnknownEntity(Entity[AnyRank, MemberT]):
    def __init__(self, rank_type: type[AnyRank], child: Entity[AnyRank, MemberT], offset: int) -> None:
        super().__init__(
            parent_key=ParentKeyStatus.NONE,
            key=self.key_from(child.key),
            member=None,
            rank=rank_type(index(child.rank) - offset),
        )

    @classmethod
    def key_from(cls, key: EntityId) -> EntityId:
        """
        Return the unknown entity ID for the given child entity ID.
        """
        return EntityId(f"{key} Parent")
