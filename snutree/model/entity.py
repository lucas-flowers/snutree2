from dataclasses import dataclass
from enum import Enum, auto
from operator import index
from typing import Generic, Optional, Type, TypeVar, Union

from snutree.model.rank import AnyRank

M = TypeVar("M")


class ParentKeyStatus(Enum):
    UNKNOWN = auto()
    NONE = auto()


class EntityId(str):
    def __new__(cls, value: str) -> "EntityId":
        return super().__new__(cls, value)


@dataclass
class Entity(Generic[AnyRank, M]):
    parent_key: Union[EntityId, ParentKeyStatus]
    key: EntityId
    rank: AnyRank
    member: Optional[M]


class CustomEntity(Entity[AnyRank, M]):
    def __init__(self, parent_key: Union[str, ParentKeyStatus], key: str, rank: AnyRank) -> None:
        super().__init__(
            parent_key=EntityId(parent_key) if isinstance(parent_key, str) else parent_key,
            key=EntityId(key),
            rank=rank,
            member=None,
        )


class UnknownEntity(Entity[AnyRank, M]):
    def __init__(self, rank_type: Type[AnyRank], child: Entity[AnyRank, M], offset: int) -> None:
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
