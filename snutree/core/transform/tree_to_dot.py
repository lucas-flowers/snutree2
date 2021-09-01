from dataclasses import dataclass
from operator import index
from typing import Optional

from snutree.core.model.common import Rank
from snutree.core.model.semester import Semester
from snutree.core.model.tree import AnyRank, Tree
from snutree.tool.dot import Attribute, Digraph, Edge, Graph, Node, Subgraph


@dataclass
class CustomConfig:
    nodes: list[Node]
    edges: list[Edge]


@dataclass
class Config:
    custom: CustomConfig


def create_family_tree(tree: Tree[AnyRank], config: Config) -> Graph:
    ranks_left_id, ranks_right_id = "ranks-left", "ranks-right"
    return Digraph(
        "family-tree",
        *create_attributes(),
        create_ranks(
            graph_id=ranks_left_id,
            ranks=tree.ranks,
        ),
        create_members(
            graph_id="members",
            tree=tree,
            custom_nodes=config.custom.nodes,
            custom_edges=config.custom.edges,
        ),
        create_ranks(
            graph_id=ranks_right_id,
            ranks=tree.ranks,
        ),
        Subgraph(
            "ranks",
            *[
                create_cohort(
                    ranks_left_id=ranks_left_id,
                    ranks_right_id=ranks_right_id,
                    rank=rank,
                    cohort=cohort,
                )
                for rank, cohort in (tree.cohorts or {}).items()
            ],
        ),
    )


def create_attributes() -> list[Attribute]:
    return []


def create_ranks(graph_id: str, ranks: Optional[list[AnyRank]]) -> Optional[Subgraph]:
    return (
        Subgraph(
            graph_id,
            *create_attributes(),
            *create_rank_nodes(graph_id, ranks),
            *create_rank_edges(graph_id, ranks),
        )
        if ranks is not None
        else None
    )


def create_rank_nodes(prefix: str, ranks: Optional[list[AnyRank]]) -> list[Node]:
    return [
        Node(
            create_rank_identifier(
                prefix=prefix,
                rank=rank,
            )
        )
        for rank in ranks or []
    ]


def create_rank_edges(prefix: str, ranks: Optional[list[AnyRank]]) -> list[Edge]:
    ranks = ranks or []
    return [
        Edge(
            create_rank_identifier(prefix, rank0),
            create_rank_identifier(prefix, rank1),
        )
        for rank0, rank1 in zip(ranks[:-1], ranks[1:])
    ]


def create_rank_identifier(prefix: str, rank: AnyRank) -> str:
    if isinstance(rank, Semester):
        suffix = str(rank).replace(" ", "").lower()
    else:
        suffix = str(index(rank))
    return f"{prefix}:{suffix}"


def create_members(graph_id: str, tree: Tree[AnyRank], custom_nodes: list[Node], custom_edges: list[Edge]) -> Subgraph:
    return Subgraph(
        graph_id,
        *create_attributes(),
        *create_nodes(tree.entity_ids),
        *custom_nodes,
        *create_edges(tree.relationship_ids),
        *custom_edges,
    )


def create_nodes(entities: list[str]) -> list[Node]:
    return [Node(entity_id) for entity_id in entities]


def create_edges(relationships: list[tuple[str, str]]) -> list[Edge]:
    return [Edge(parent_id, child_id) for parent_id, child_id in relationships]


def create_cohort(ranks_left_id: str, ranks_right_id: str, rank: Rank, cohort: set[str]) -> Subgraph:
    return Subgraph(
        Node(create_rank_identifier(ranks_left_id, rank)),
        Node(create_rank_identifier(ranks_right_id, rank)),
        *[Node(entity_id) for entity_id in sorted(cohort)],
    )
