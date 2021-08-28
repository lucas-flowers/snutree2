"""
Functions to declaratively create DOT objects.
"""

# pylint: disable=invalid-name,keyword-arg-before-vararg

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union, overload

from snutree.tool.dot.model import (
    _Attribute,
    _AttrValue,
    _Component,
    _ComponentType,
    _Graph,
    _GraphType,
    _Statement,
)


class NullStatementType(Enum):
    INSTANCE = object()


NULL_STMT = NullStatementType.INSTANCE


# Since statements can be None, we need to use a sentinel type to signify no statements
OptionalStatement = Union[_Statement, NullStatementType]


@dataclass
class GraphFactory:

    graph_type: _GraphType

    @overload
    def __call__(self, identifier: str, /, *statements: _Statement) -> _Graph:
        ...

    @overload
    def __call__(self, /, *statements: _Statement) -> _Graph:
        ...

    def __call__(self, arg: Union[str, OptionalStatement] = NULL_STMT, /, *args: _Statement) -> _Graph:
        identifier: Optional[str]
        if arg is NULL_STMT:
            identifier, statements = None, args
        elif isinstance(arg, str):
            identifier, statements = arg, args
        else:
            identifier, statements = None, (arg, *args)
        return _Graph(self.graph_type, identifier, list(statements))


StrictGraph = GraphFactory(_GraphType.STRICT_GRAPH)
StrictDigraph = GraphFactory(_GraphType.STRICT_DIGRAPH)
Digraph = GraphFactory(_GraphType.DIGRAPH)


@overload
def Graph(**attributes: _AttrValue) -> _Statement:
    ...


@overload
def Graph(*statements: _Statement) -> _Statement:
    ...


@overload
def Graph(identifier: str, /, *statements: _Statement) -> _Statement:
    ...


def Graph(arg: Union[str, OptionalStatement] = NULL_STMT, /, *args: _Statement, **kwargs: _AttrValue) -> _Statement:
    if kwargs:
        return _Component(_ComponentType.GRAPH, [], _Attribute.from_dict(kwargs))
    elif arg is NULL_STMT:
        return GraphFactory(_GraphType.GRAPH)(*args)
    else:
        return GraphFactory(_GraphType.GRAPH)(arg, *args)


@overload
def Subgraph(identifier: str, /, *statements: _Statement) -> _Statement:
    ...


@overload
def Subgraph(*statements: _Statement) -> _Statement:
    ...


def Subgraph(arg: Union[str, OptionalStatement] = NULL_STMT, /, *args: _Statement) -> _Statement:
    graph_type: Optional[_GraphType]
    identifier: Optional[str]
    if arg is NULL_STMT:
        graph_type, identifier, statements = None, None, args
    elif isinstance(arg, str):
        graph_type, identifier, statements = _GraphType.SUBGRAPH, arg, args
    else:
        graph_type, identifier, statements = None, None, (arg, *args)
    return _Graph(graph_type, identifier, list(statements))


def Node(identifier: Optional[str] = None, /, **attributes: _AttrValue) -> _Statement:
    identifiers = [] if identifier is None else [identifier]
    return _Component(_ComponentType.NODE, identifiers, _Attribute.from_dict(attributes))


@overload
def Edge(**attributes: _AttrValue) -> _Statement:
    ...


@overload
def Edge(id1: str, id2: str, /, *ids: str, **attributes: _AttrValue) -> _Statement:
    ...


def Edge(arg1: Optional[str] = None, arg2: Optional[str] = None, /, *args: str, **attributes: _AttrValue) -> _Statement:
    if arg1 is None and arg2 is None:
        identifiers = args
    elif arg1 is not None and arg2 is not None:
        identifiers = (arg1, arg2, *args)
    else:  # pragma: no cover
        raise RuntimeError("Check function overloading")
    return _Component(_ComponentType.EDGE, list(identifiers), _Attribute.from_dict(attributes))


@overload
def Attribute(key: str, value: _AttrValue, /) -> _Statement:
    ...


@overload
def Attribute(**kwargs: _AttrValue) -> _Statement:
    ...


def Attribute(key: Optional[str] = None, value: Optional[_AttrValue] = None, /, **kwargs: _AttrValue) -> _Statement:
    if len(kwargs) > 1:
        raise ValueError("Only a single kwarg is permitted")
    elif len(kwargs) == 1:
        return _Attribute(*kwargs.popitem())
    else:
        if key is None or value is None:
            raise ValueError("Must provide a key and a value")
        else:
            return _Attribute(key, value)
