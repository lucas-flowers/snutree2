from typing import Optional, Protocol, TypeVar, runtime_checkable

AnyRank = TypeVar("AnyRank", bound="Rank")


@runtime_checkable
class Rank(Protocol):
    def __init__(self, i: Optional[int] = None, /) -> None:  # pylint: disable=super-init-not-called
        ...

    def __index__(self) -> int:  # pylint: disable=invalid-index-returned # Come on pylint, it's a protocol
        ...
