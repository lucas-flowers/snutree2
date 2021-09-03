from dataclasses import dataclass, field
from operator import index
from typing import Callable, Generic, Optional, TypeVar

from snutree.model.semester import Semester
from snutree.model.tree import AnyRank, Tree
from snutree.tool.dot import (
    Attribute,
    Digraph,
    Edge,
    Graph,
    Id,
    Node,
    Subgraph,
)

E = TypeVar("E")
R = TypeVar("R")


@dataclass
class NamesConfig:
    root = "family-tree"
    members = "members"
    ranks = "ranks"
    ranks_left = "ranks-left"
    ranks_right = "ranks-right"


@dataclass
class DefaultAttributesConfig:
    root: dict[str, Id] = field(default_factory=dict)
    member: dict[str, Id] = field(default_factory=dict)
    rank: dict[str, Id] = field(default_factory=dict)


@dataclass
class DynamicNodeAttributesConfig(Generic[AnyRank, E]):
    member: Callable[[E], dict[str, Id]] = lambda _: {}
    rank: Callable[[AnyRank], dict[str, Id]] = lambda _: {}
    family: Callable[[str], dict[str, Id]] = lambda _: {}


@dataclass
class GraphsConfig:
    names: NamesConfig = field(default_factory=NamesConfig)
    defaults: DefaultAttributesConfig = field(default_factory=DefaultAttributesConfig)


@dataclass
class NodesConfig(Generic[AnyRank, E]):
    defaults: DefaultAttributesConfig = field(default_factory=DefaultAttributesConfig)
    attributes: DynamicNodeAttributesConfig[AnyRank, E] = field(default_factory=DynamicNodeAttributesConfig)
    custom: list[Node] = field(default_factory=list)


@dataclass
class EdgesConfig(Generic[R]):
    defaults: DefaultAttributesConfig = field(default_factory=DefaultAttributesConfig)
    custom: list[Edge] = field(default_factory=list)


@dataclass
class DotWriterConfig(Generic[E, R, AnyRank]):
    graph: GraphsConfig = field(default_factory=GraphsConfig)
    node: NodesConfig[AnyRank, E] = field(default_factory=NodesConfig)
    edge: EdgesConfig[R] = field(default_factory=EdgesConfig)


@dataclass
class DotWriter(Generic[E, R, AnyRank]):

    # pylint: disable=no-self-use

    config: DotWriterConfig[E, R, AnyRank] = field(default_factory=DotWriterConfig)

    def write_family_tree(self, tree: Tree[E, R, AnyRank]) -> Graph:
        return Digraph(
            self.config.graph.names.root,
            *self.write_graph_defaults(self.config.graph.defaults.root),
            self.write_node_defaults(self.config.node.defaults.root),
            self.write_edge_defaults(self.config.edge.defaults.root),
            self.write_ranks(
                graph_id=self.config.graph.names.ranks_left,
                ranks=tree.ranks,
            ),
            self.write_members(
                graph_id=self.config.graph.names.members,
                tree=tree,
            ),
            self.write_ranks(
                graph_id=self.config.graph.names.ranks_right,
                ranks=tree.ranks,
            ),
            Subgraph(
                self.config.graph.names.ranks,
                *[
                    self.write_cohort(
                        rank=rank,
                        cohort=cohort,
                    )
                    for rank, cohort in (tree.cohorts or {}).items()
                ],
            ),
        )

    def write_graph_defaults(self, attributes: dict[str, Id]) -> list[Attribute]:
        return [Attribute(key, value) for key, value in attributes.items()]

    def write_node_defaults(self, attributes: dict[str, Id]) -> Optional[Node]:
        return None if not attributes else Node(**attributes)

    def write_edge_defaults(self, attributes: dict[str, Id]) -> Optional[Edge]:
        return None if not attributes else Edge(**attributes)

    def write_ranks(self, graph_id: str, ranks: Optional[list[AnyRank]]) -> Optional[Subgraph]:
        return (
            Subgraph(
                graph_id,
                *self.write_graph_defaults(self.config.graph.defaults.rank),
                self.write_node_defaults(self.config.node.defaults.rank),
                self.write_edge_defaults(self.config.edge.defaults.rank),
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
                ),
                **self.config.node.attributes.rank(rank),
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
            *self.write_graph_defaults(self.config.graph.defaults.member),
            self.write_node_defaults(self.config.node.defaults.member),
            self.write_edge_defaults(self.config.edge.defaults.member),
            *self.write_nodes(tree.entities, tree.families),
            *self.config.node.custom,
            *self.write_edges(tree.relationships),
            *self.config.edge.custom,
        )

    def write_nodes(self, entities: dict[str, E], families: dict[str, str]) -> list[Node]:
        return [
            Node(
                entity_id,
                **self.config.node.attributes.member(entity),
                **(self.config.node.attributes.family(families[entity_id]) if entity_id in families else {}),
            )
            for entity_id, entity in entities.items()
        ]

    def write_edges(self, relationships: dict[tuple[str, str], R]) -> list[Edge]:
        return [
            Edge(
                *relationship_id,
            )
            for relationship_id, relationship in relationships.items()
        ]

    def write_cohort(self, rank: AnyRank, cohort: set[str]) -> Subgraph:
        return Subgraph(
            Attribute(rank="same"),
            Node(self.write_rank_identifier(self.config.graph.names.ranks_left, rank)),
            Node(self.write_rank_identifier(self.config.graph.names.ranks_right, rank)),
            *[Node(entity_id) for entity_id in sorted(cohort)],
        )
