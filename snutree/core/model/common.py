from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class Rank(Protocol):
    def __init__(self, index: Optional[int] = None, /) -> None:  # pylint: disable=super-init-not-called
        ...

    def __index__(self) -> int:  # pylint: disable=invalid-index-returned # Come on pylint, it's a protocol
        ...
