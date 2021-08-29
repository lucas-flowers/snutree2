from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, TypeVar, Union

from snutree.core.model.common import Component, Rank

OptionalAnyRank = TypeVar("OptionalAnyRank", bound=Union[Rank, None])


class ParentStatus(Enum):
    UNKNOWN = auto()
    NONE = auto()


@dataclass
class Member(Component, Generic[OptionalAnyRank]):
    id: str
    parent_id: Union[str, ParentStatus]
    rank: OptionalAnyRank
