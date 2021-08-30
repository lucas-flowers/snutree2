"""
Underlying representations of DOT objects.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Iterator, Optional, Union

_Statement = Union[
    "Attr",
    "_Component",
    "_Graph",
    None,
]


@dataclass(init=False)
class _Block:

    blocks: list[Union[str, "_Block"]]

    TAB_STOP = 4
    TAB_CHAR = " "

    def __init__(self, *subblocks: Union[str, "_Block"]) -> None:
        self.subblocks = list(subblocks)

    def __iter__(self) -> Iterator[Union[str, "_Block"]]:
        yield from self.subblocks

    def lines(self, level: int) -> Iterable[str]:
        indent = level * self.TAB_STOP * self.TAB_CHAR
        for block in self.subblocks:
            if isinstance(block, _Block):
                yield from block.lines(level + 1)
            else:
                yield f"{indent}{block}\n"


class _StringEnum(Enum):
    def __str__(self) -> str:
        value: object = self.value
        return str(value)


class _ComponentType(_StringEnum):
    GRAPH = "graph"
    NODE = "node"
    EDGE = "edge"


class _EdgeOp(_StringEnum):
    DIRECTED = " -> "
    UNDIRECTED = " -- "


class _GraphType(_StringEnum):
    GRAPH = "graph"
    DIGRAPH = "digraph"
    SUBGRAPH = "subgraph"
    STRICT_DIGRAPH = "strict digraph"
    STRICT_GRAPH = "strict graph"


Id = Union[str, int, float]


@dataclass
class Attr:

    id: Id
    value: Id

    @classmethod
    def from_dict(cls, mapping: dict[str, Id]) -> list["Attr"]:
        return [Attr(key, value) for key, value in mapping.items()]

    @property
    def block(self) -> _Block:
        return _Block(str(self) + ";")

    def __str__(self) -> str:
        return (
            f'{self.id}="{self.value}"'
            if isinstance(self.value, str) and not re.match(r"^<.+>$", self.value)
            else f"{self.id}={self.value}"
        )


@dataclass
class _Component:

    type: _ComponentType
    identifiers: list[str]
    attributes: list[Attr]

    EDGE_OP = _EdgeOp.DIRECTED

    @property
    def block(self) -> _Block:
        return _Block(str(self) + ";")

    def __str__(self) -> str:

        identifiers: list[Union[str, _ComponentType]]
        if is_attribute_statement := not bool(self.identifiers):
            identifiers = [self.type]
        else:
            identifiers = list(self.identifiers)

        identifier = str(self.EDGE_OP).join(
            str(identifier) if isinstance(identifier, _ComponentType) else f'"{identifier}"'
            for identifier in identifiers
        )

        attributes = ",".join(map(str, self.attributes))

        if attributes or is_attribute_statement:
            return f"{identifier} [{attributes}]"
        else:
            return identifier


@dataclass
class _Graph:

    graph_type: Optional[_GraphType]
    identifier: Optional[str]
    statements: list[_Statement]

    TAB_STOP = 4
    TAB_CHAR = " "

    @property
    def block(self) -> _Block:

        if not self.graph_type and not self.identifier:
            begin = "{"
        elif not self.identifier:
            begin = f"{self.graph_type} {{"
        else:
            assert self.graph_type is not None
            begin = f'{self.graph_type} "{self.identifier}" {{'

        subblocks = [subblock for statement in self.statements if statement for subblock in statement.block]

        end = "}"

        return _Block(begin, _Block(*subblocks), end)

    def __str__(self) -> str:
        return "".join(self.block.lines(level=0))
