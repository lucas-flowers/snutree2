import re
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import (
    Iterable,
    Iterator,
    Optional,
    Protocol,
    Union,
    overload,
    runtime_checkable,
)

Id = Union[str, int, float]


class NullStatementType(Enum):
    INSTANCE = object()


NULL_STMT = NullStatementType.INSTANCE


@dataclass(init=False)
class Block:

    blocks: list[Union[str, "Block"]]

    TAB_STOP = 4
    TAB_CHAR = " "

    def __init__(self, *subblocks: Union[str, "Block"]) -> None:
        self.subblocks = list(subblocks)

    def __iter__(self) -> Iterator[Union[str, "Block"]]:
        yield from self.subblocks

    def lines(self, level: int) -> Iterable[str]:
        indent = level * self.TAB_STOP * self.TAB_CHAR
        for block in self.subblocks:
            if isinstance(block, Block):
                yield from block.lines(level + 1)
            else:
                yield f"{indent}{block}\n"


@runtime_checkable
class Statement(Protocol):
    @property
    def block(self) -> Block:
        ...


class EdgeOp(Enum):

    DIRECTED = " -> "
    UNDIRECTED = " -- "

    def __str__(self) -> str:
        value: object = self.value
        return str(value)


@dataclass
class Component(ABC):
    """
    Represent a DOT node or edge.
    """

    ids: list[Id]
    attrs: list["Attribute"]

    EDGE_OP = EdgeOp.DIRECTED

    @property
    def block(self) -> Block:
        return Block(str(self) + ";")

    def __str__(self) -> str:

        ids: list[str]
        if is_attribute_statement := not bool(self.ids):
            ids = [type(self).__name__.lower()]
        else:
            ids = [f'"{identifier}"' for identifier in self.ids]

        identifier = str(self.EDGE_OP).join(ids)

        attrs = ",".join(map(str, self.attrs))

        if attrs or is_attribute_statement:
            return f"{identifier} [{attrs}]"
        else:
            return identifier


@dataclass
class Attribute:

    key: Id
    value: Id

    @overload
    def __init__(self, key: Id, value: Id, /) -> None:
        ...

    @overload
    def __init__(self, /, **kwargs: Id) -> None:
        ...

    def __init__(self, key: Optional[Id] = None, value: Optional[Id] = None, /, **kwargs: Id) -> None:
        if len(kwargs) > 1:
            raise ValueError("Only a single kwarg is permitted")
        elif len(kwargs) == 1:
            self.key, self.value = kwargs.popitem()
        else:
            if key is None or value is None:
                raise ValueError("Must provide a key and a value")
            else:
                self.key, self.value = key, value

    @classmethod
    def from_kwargs(cls, **mapping: Id) -> list["Attribute"]:
        return [Attribute(key, value) for key, value in mapping.items()]

    @property
    def block(self) -> Block:
        return Block(str(self) + ";")

    def __str__(self) -> str:
        return (
            f'{self.key}="{self.value}"'
            if isinstance(self.value, str) and not re.match(r"^<.+>$", self.value)
            else f"{self.key}={self.value}"
        )


class Node(Component):
    """
    Represent a DOT node.
    """

    def __init__(self, identifier: Optional[Id] = None, /, **attrs: Id) -> None:
        ids = [] if identifier is None else [identifier]
        super().__init__(ids, Attribute.from_kwargs(**attrs))


class Edge(Component):
    """
    Represent a DOT edge.
    """

    @overload
    def __init__(self, /, **attributes: Id) -> None:
        ...

    @overload
    def __init__(self, id1: Id, id2: Id, /, *ids: Id, **attributes: Id) -> None:
        ...

    def __init__(self, arg1: Optional[Id] = None, arg2: Optional[Id] = None, /, *args: Id, **attributes: Id) -> None:
        if arg1 is None and arg2 is None:
            identifiers = args
        elif arg1 is not None and arg2 is not None:
            identifiers = (arg1, arg2, *args)
        else:  # pragma: no cover
            raise RuntimeError("Check function overloading")
        super().__init__(list(identifiers), Attribute.from_kwargs(**attributes))


@dataclass
class Graph:
    """
    Represent a DOT graph.
    """

    identifier: Optional[Id]
    statements: list[Statement]
    graph_type: str = "graph"

    TAB_STOP = 4
    TAB_CHAR = " "

    @overload
    def __init__(self, identifier: Id, /, *statements: Optional[Statement]) -> None:
        ...

    @overload
    def __init__(self, /, *statements: Optional[Statement]) -> None:
        ...

    def __init__(
        self, arg: Union[Id, Optional[Statement], NullStatementType] = NULL_STMT, /, *args: Optional[Statement]
    ) -> None:

        identifier: Optional[Id]
        if arg is NULL_STMT:
            identifier, statements = None, args
        elif arg is not None and not isinstance(arg, Statement):
            identifier, statements = arg, args
        else:
            identifier, statements = None, (arg, *args)

        self.identifier = identifier
        self.statements = [statement for statement in statements if statement]

    @property
    def block(self) -> Block:

        if not self.identifier:
            begin = str(self.graph_type) + " {"
        else:
            begin = f'{self.graph_type} "{self.identifier}"' + " {"

        subblocks = [subblock for statement in self.statements if statement for subblock in statement.block]

        end = "}"

        return Block(begin, Block(*subblocks), end)

    def __str__(self) -> str:
        return "".join(self.block.lines(level=0))


class StrictGraph(Graph):
    graph_type = "strict graph"


class Digraph(Graph):
    graph_type = "digraph"


class StrictDigraph(Graph):
    graph_type = "strict digraph"


class Subgraph(Graph):
    graph_type = "subgraph"
