from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, Optional, TypeVar, Union

from snutree.core.model.common import Component, Rank

OptionalAnyRank = TypeVar("OptionalAnyRank", bound=Union[Rank, None])


class RankStatus(Enum):
    UNKNOWN = auto()


@dataclass
class Entity(Generic[OptionalAnyRank]):
    rank: Union[OptionalAnyRank, RankStatus]


class Relationship(Component):
    pass


@dataclass
class FamilyTree(Component, Generic[OptionalAnyRank]):
    entities: dict[str, Entity[OptionalAnyRank]]
    relationships: dict[tuple[Optional[str], str], Relationship]
    ranks: set[OptionalAnyRank]
