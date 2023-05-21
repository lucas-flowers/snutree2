from typing import TypeVar

from networkx import DiGraph

# pylint: disable=unused-argument

T = TypeVar("T")

def freeze(G: DiGraph[T]) -> DiGraph[T]: ...
