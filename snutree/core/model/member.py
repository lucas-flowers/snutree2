from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Generic, SupportsIndex, TypeVar, Union

# Rank types may either be integral or NoneType
R = TypeVar("R", SupportsIndex, None)


class ParentStatus(Enum):
    UNKNOWN = auto()
    NONE = auto()


@dataclass
class Member(Generic[R]):
    id: str
    parent_id: Union[str, ParentStatus]
    rank: R
    classes: list[str] = field(default_factory=list)
    data: dict[str, str] = field(default_factory=dict)
