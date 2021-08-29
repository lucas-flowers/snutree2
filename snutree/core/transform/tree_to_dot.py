from dataclasses import dataclass
from operator import index
from typing import Optional, TypeVar

from snutree.core.model.common import Rank
from snutree.core.model.semester import Semester
from snutree.core.model.tree import Cohort, Tree
from snutree.tool.dot.declarative import Digraph, Edge, Node, Subgraph
from snutree.tool.dot.model import _Statement

T = TypeVar("T")


@dataclass
class NameConfig:
    root_graph: str
    ranks_graph_left: str
    ranks_graph_right: str
    tree_graph: str


@dataclass
class CustomConfig:
    nodes: list[_Statement]
    edges: list[_Statement]


@dataclass
class Config:
    names: NameConfig
    custom: CustomConfig


def create_root(tree: Tree[T], config: Config) -> _Statement:
    return Digraph(
        config.names.root_graph,
        *create_attributes(),
        create_ranks(
            graph_id=config.names.ranks_graph_left,
            ranks=tree.ranks,
        ),
        create_tree(
            graph_id=config.names.tree_graph,
            tree=tree,
            custom_nodes=config.custom.nodes,
            custom_edges=config.custom.edges,
        ),
        create_ranks(
            graph_id=config.names.ranks_graph_right,
            ranks=tree.ranks,
        ),
        *map(create_cohort, tree.cohorts or []),
    )


# pylint: disable=unused-argument


def create_attributes() -> list[_Statement]:
    ...


def create_ranks(graph_id: str, ranks: Optional[tuple[Rank, Rank]]) -> Optional[_Statement]:
    return (
        Subgraph(
            graph_id,
            *create_attributes(),
            *create_rank_nodes(graph_id, *ranks),
            *create_rank_edges(graph_id, *ranks),
        )
        if ranks is not None
        else None
    )


def create_rank_nodes(prefix: str, start: Rank, stop: Rank) -> list[_Statement]:
    rank_type = type(start)
    return [
        Node(
            create_rank_identifier(
                prefix=prefix,
                rank=rank_type(i),
            )
        )
        for i in range(index(start), index(stop) + 1)
    ]


def create_rank_edges(prefix: str, start: Rank, stop: Rank) -> list[_Statement]:
    rank_type = type(start)
    return [
        Edge(
            create_rank_identifier(prefix, rank_type(i)),
            create_rank_identifier(prefix, rank_type(i + 1)),
        )
        for i in range(index(start), index(stop))
    ]


def create_rank_identifier(prefix: str, rank: Rank) -> str:
    if isinstance(rank, Semester):
        suffix = str(rank).replace(" ", "").lower()
    else:
        suffix = str(index(rank))
    return f"{prefix}:{suffix}"


def create_tree(
    graph_id: str, tree: Tree[T], custom_nodes: list[_Statement], custom_edges: list[_Statement]
) -> _Statement:
    return Subgraph(
        graph_id,
        *create_attributes(),
        *create_nodes(tree),
        *custom_nodes,
        *create_edges(tree),
        *custom_edges,
    )


def create_nodes(tree: Tree[T]) -> list[_Statement]:
    ...


def create_edges(tree: Tree[T]) -> list[_Statement]:
    ...


def create_cohort(cohort: Cohort) -> _Statement:
    ...
