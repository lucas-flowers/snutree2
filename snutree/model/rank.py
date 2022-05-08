from typing import Optional, Protocol, TypeVar, runtime_checkable

AnyRank = TypeVar("AnyRank", bound="Rank")


@runtime_checkable
class Rank(Protocol):
    def __init__(self, i: Optional[int] = None, /) -> None:
        ...

    def __index__(self) -> int:
        ...
