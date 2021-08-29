from dataclasses import dataclass
from typing import Protocol, TypeVar, Union, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Rank(Protocol):

    # # pylint: disable=invalid-index-returned # Come on pylint, it's a protocol
    def __index__(self) -> int:
        ...

    def __add__(self: T, other: int) -> T:
        ...

    def __sub__(self: T, other: Union[T, int]) -> T:
        ...

    def __gt__(self: T, other: T) -> bool:
        ...

    def __lt__(self: T, other: T) -> bool:
        ...

    def __le__(self: T, other: T) -> bool:
        ...

    def __ge__(self: T, other: T) -> bool:
        ...


@dataclass
class Component:
    classes: list[str]
    data: dict[str, str]
