from typing import Iterable, TypeVar

from networkx import DiGraph

# pylint: disable=unused-argument,multiple-statements

T = TypeVar("T")

def compose_all(graphs: Iterable[DiGraph[T]]) -> DiGraph[T]: ...
