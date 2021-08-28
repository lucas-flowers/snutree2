from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, Union

from snutree.core.model.common import AnyRank, Component


class ParentStatus(Enum):
    UNKNOWN = auto()
    NONE = auto()


@dataclass
class Member(Component, Generic[AnyRank]):
    id: str
    parent_id: Union[str, ParentStatus]
    rank: AnyRank
