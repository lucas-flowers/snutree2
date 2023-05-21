from typing import Protocol, TypeVar, runtime_checkable

AnyRank = TypeVar("AnyRank", bound="Rank")


@runtime_checkable
class Rank(Protocol):
    def __init__(self, i: int | None = None, /) -> None:
        ...

    def __index__(self) -> int:
        ...
