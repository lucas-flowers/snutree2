from typing import TypeVar

from networkx import DiGraph

# pylint: disable=unused-argument,multiple-statements

T = TypeVar("T")

def freeze(G: DiGraph[T]) -> DiGraph[T]: ...
