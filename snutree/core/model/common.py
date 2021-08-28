from dataclasses import dataclass
from typing import SupportsIndex, TypeVar

# Rank types may either be integral or NoneType
AnyRank = TypeVar("AnyRank", SupportsIndex, None)


@dataclass
class Component:
    classes: list[str]
    data: dict[str, str]
