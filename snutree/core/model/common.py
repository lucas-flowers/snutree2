from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class Rank(Protocol):
    def __init__(self, index: int, /) -> None:  # pylint: disable=super-init-not-called
        ...

    def __index__(self) -> int:  # pylint: disable=invalid-index-returned # Come on pylint, it's a protocol
        ...


@dataclass
class Component:
    classes: list[str]
    data: dict[str, str]
