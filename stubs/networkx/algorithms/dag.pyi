from typing import TypeVar

from networkx import DiGraph

# pylint: disable=multiple-statements,unused-argument

T = TypeVar("T")

def descendants(G: DiGraph[T], source: T) -> set[T]: ...
