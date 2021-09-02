from dataclasses import dataclass, field
from operator import index
from typing import Optional, Protocol, TypeVar

from snutree.core.model.common import Rank
from snutree.core.model.semester import Semester
from snutree.core.model.tree import AnyRank, Entity, Relationship, Tree
from snutree.tool.dot import (
    Attribute,
    Digraph,
    Edge,
    Graph,
    Id,
    Node,
    Subgraph,
)

E = TypeVar("E", bound="DotComponent")
R = TypeVar("R", bound="DotComponent")


class DotComponent(Protocol):
    # TODO: Decided whether to keep this a protocol, or make it a callable
    # injected into the DotWriter configuration
    @property
    def dot_attributes(self) -> dict[str, Id]:
        ...


@dataclass
class CustomComponentConfig:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


@dataclass
class NamesConfig:
    root = "family-tree"
    members = "members"
    ranks = "ranks"
    ranks_left = "ranks-left"
    ranks_right = "ranks-right"


@dataclass
class DotWriterConfig:
    custom: CustomComponentConfig = field(default_factory=CustomComponentConfig)
    names: NamesConfig = field(default_factory=NamesConfig)


@dataclass
class DotWriter:

    # pylint: disable=no-self-use

    config: DotWriterConfig = field(default_factory=DotWriterConfig)

    def write_family_tree(self, tree: Tree[E, R, AnyRank]) -> Graph:
        ranks_left_id, ranks_right_id = "ranks-left", "ranks-right"
        return Digraph(
            self.config.names.root,
            *self.write_attributes(),
            self.write_ranks(
                graph_id=ranks_left_id,
                ranks=tree.ranks,
            ),
            self.write_members(
                graph_id=self.config.names.members,
                tree=tree,
            ),
            self.write_ranks(
                graph_id=ranks_right_id,
                ranks=tree.ranks,
            ),
            Subgraph(
                self.config.names.ranks,
                *[
                    self.write_cohort(
                        rank=rank,
                        cohort=cohort,
                    )
                    for rank, cohort in (tree.cohorts or {}).items()
                ],
            ),
        )

    def write_attributes(self) -> list[Attribute]:
        return []

    def write_ranks(self, graph_id: str, ranks: Optional[list[AnyRank]]) -> Optional[Subgraph]:
        return (
            Subgraph(
                graph_id,
                *self.write_attributes(),
                *self.write_rank_nodes(graph_id, ranks),
                *self.write_rank_edges(graph_id, ranks),
            )
            if ranks is not None
            else None
        )

    def write_rank_nodes(self, prefix: str, ranks: Optional[list[AnyRank]]) -> list[Node]:
        return [
            Node(
                self.write_rank_identifier(
                    prefix=prefix,
                    rank=rank,
                )
            )
            for rank in ranks or []
        ]

    def write_rank_edges(self, prefix: str, ranks: Optional[list[AnyRank]]) -> list[Edge]:
        ranks = ranks or []
        return [
            Edge(
                self.write_rank_identifier(prefix, rank0),
                self.write_rank_identifier(prefix, rank1),
            )
            for rank0, rank1 in zip(ranks[:-1], ranks[1:])
        ]

    def write_rank_identifier(self, prefix: str, rank: AnyRank) -> str:
        if isinstance(rank, Semester):
            suffix = str(rank).replace(" ", "").lower()
        else:
            suffix = str(index(rank))
        return f"{prefix}:{suffix}"

    def write_members(self, graph_id: str, tree: Tree[E, R, AnyRank]) -> Subgraph:
        return Subgraph(
            graph_id,
            *self.write_attributes(),
            *self.write_nodes(tree.entities),
            *self.config.custom.nodes,
            *self.write_edges(tree.relationships),
            *self.config.custom.edges,
        )

    def write_nodes(self, entities: dict[str, Entity[E, AnyRank]]) -> list[Node]:
        return [
            Node(
                entity_id,
                **entity.payload.dot_attributes,
            )
            for entity_id, entity in entities.items()
        ]

    def write_edges(self, relationships: dict[tuple[str, str], Relationship[R]]) -> list[Edge]:
        return [
            Edge(
                *relationship_id,
                **relationship.payload.dot_attributes,
            )
            for relationship_id, relationship in relationships.items()
        ]

    def write_cohort(self, rank: Rank, cohort: set[str]) -> Subgraph:
        return Subgraph(
            Node(self.write_rank_identifier(self.config.names.ranks_left, rank)),
            Node(self.write_rank_identifier(self.config.names.ranks_right, rank)),
            *[Node(entity_id) for entity_id in sorted(cohort)],
        )
