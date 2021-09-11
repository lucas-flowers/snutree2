from dataclasses import dataclass, field
from operator import index
from typing import Callable, Dict, Generic, Optional, TypeVar

from snutree.model.semester import Semester
from snutree.model.tree import AnyRank, Entity, FamilyTree
from snutree.tool.dot import (
    Attribute,
    Digraph,
    Edge,
    Graph,
    Id,
    Node,
    Subgraph,
)

M = TypeVar("M")


@dataclass
class NamesConfig:
    root = "family_tree"
    entities = "members"
    ranks = "ranks"
    ranks_left = "datesL"
    ranks_right = "datesR"


@dataclass
class DefaultAttributesConfig:
    root: dict[str, Id] = field(default_factory=dict)
    entity: dict[str, Id] = field(default_factory=dict)
    rank: dict[str, Id] = field(default_factory=dict)


@dataclass
class DefaultNodeAttributesConfig(DefaultAttributesConfig):
    unknown: dict[str, Id] = field(default_factory=dict)


@dataclass
class DefaultEdgeAttributesConfig(DefaultAttributesConfig):
    unknown: dict[str, Id] = field(default_factory=dict)


@dataclass
class DynamicNodeAttributesConfig(Generic[AnyRank, M]):
    rank: Callable[[AnyRank], dict[str, Id]] = lambda _: {}
    entity: Callable[[Entity[AnyRank, M]], dict[str, Id]] = lambda _: {}
    member: Callable[[M], dict[str, Id]] = lambda _: {}
    family: Callable[[str], dict[str, Id]] = lambda _: {}
    by_key: Dict[str, dict[str, Id]] = field(default_factory=dict)


@dataclass
class DynamicEdgeAttributesConfig:
    by_key: Dict[tuple[str, str], dict[str, Id]] = field(default_factory=dict)


@dataclass
class GraphsConfig:
    names: NamesConfig = field(default_factory=NamesConfig)
    defaults: DefaultAttributesConfig = field(default_factory=DefaultAttributesConfig)


@dataclass
class NodesConfig(Generic[AnyRank, M]):
    defaults: DefaultNodeAttributesConfig = field(default_factory=DefaultNodeAttributesConfig)
    attributes: DynamicNodeAttributesConfig[AnyRank, M] = field(default_factory=DynamicNodeAttributesConfig)
    custom: list[Node] = field(default_factory=list)


@dataclass
class EdgesConfig:
    defaults: DefaultEdgeAttributesConfig = field(default_factory=DefaultEdgeAttributesConfig)
    attributes: DynamicEdgeAttributesConfig = field(default_factory=DynamicEdgeAttributesConfig)
    custom: list[Edge] = field(default_factory=list)


@dataclass
class DotWriterConfig(Generic[AnyRank, M]):
    draw_ranks: bool = True
    graph: GraphsConfig = field(default_factory=GraphsConfig)
    node: NodesConfig[AnyRank, M] = field(default_factory=NodesConfig)
    edge: EdgesConfig = field(default_factory=EdgesConfig)


@dataclass
class DotWriter(Generic[AnyRank, M]):

    config: DotWriterConfig[AnyRank, M] = field(default_factory=DotWriterConfig)

    def write(self, tree: FamilyTree[AnyRank, M]) -> str:
        return str(self.write_family_tree(tree))

    def write_family_tree(self, tree: FamilyTree[AnyRank, M]) -> Graph:

        ranks: Optional[list[AnyRank]]
        cohorts: Optional[dict[AnyRank, set[str]]]
        if self.config.draw_ranks:
            ranks = tree.ranks
            cohorts = tree.cohorts
        else:
            ranks = None
            cohorts = None

        return Digraph(
            self.config.graph.names.root,
            *self.write_graph_defaults(self.config.graph.defaults.root),
            self.write_node_defaults(self.config.node.defaults.root),
            self.write_edge_defaults(self.config.edge.defaults.root),
            self.write_ranks(self.config.graph.names.ranks_left, ranks, "L"),
            self.write_entities(self.config.graph.names.entities, tree),
            self.write_ranks(self.config.graph.names.ranks_right, ranks, "R"),
            self.write_cohorts(cohorts),
        )

    def write_graph_defaults(self, attributes: dict[str, Id]) -> list[Attribute]:
        return sorted(Attribute(key, value) for key, value in attributes.items())

    def write_node_defaults(self, attributes: dict[str, Id]) -> Optional[Node]:
        return None if not attributes else Node(**attributes)

    def write_edge_defaults(self, attributes: dict[str, Id]) -> Optional[Edge]:
        return None if not attributes else Edge(**attributes)

    def write_ranks(self, graph_id: str, ranks: Optional[list[AnyRank]], suffix: str) -> Optional[Subgraph]:
        return (
            Subgraph(
                graph_id,
                *self.write_graph_defaults(self.config.graph.defaults.rank),
                self.write_node_defaults(self.config.node.defaults.rank),
                self.write_edge_defaults(self.config.edge.defaults.rank),
                *self.write_rank_nodes(graph_id, ranks, suffix),
                *self.write_rank_edges(graph_id, ranks, suffix),
            )
            if ranks is not None
            else None
        )

    def write_rank_nodes(self, prefix: str, ranks: Optional[list[AnyRank]], suffix: str) -> list[Node]:
        return [
            Node(
                self.write_rank_identifier(
                    _prefix=prefix,
                    rank=rank,
                    suffix=suffix,
                ),
                **self.config.node.attributes.rank(rank),
            )
            for rank in ranks or []
        ]

    def write_rank_edges(self, prefix: str, ranks: Optional[list[AnyRank]], suffix: str) -> list[Edge]:
        ranks = ranks or []
        return [
            Edge(
                self.write_rank_identifier(prefix, rank0, suffix),
                self.write_rank_identifier(prefix, rank1, suffix),
            )
            for rank0, rank1 in zip(ranks[:-1], ranks[1:])
        ]

    def write_rank_identifier(self, _prefix: str, rank: AnyRank, suffix: str) -> str:
        if isinstance(rank, Semester):
            infix = str(rank)
        else:
            infix = str(index(rank))
        return f"{infix}{suffix}"

    def write_entities(self, graph_id: str, tree: FamilyTree[AnyRank, M]) -> Subgraph:
        return Subgraph(
            graph_id,
            *self.write_graph_defaults(self.config.graph.defaults.entity),
            self.write_node_defaults(self.config.node.defaults.entity),
            self.write_edge_defaults(self.config.edge.defaults.entity),
            *self.write_nodes(tree),
            *self.config.node.custom,
            *self.write_edges(tree),
            *self.config.edge.custom,
        )

    def write_nodes(self, tree: FamilyTree[AnyRank, M]) -> list[Node]:
        return [
            Node(
                entity.key,
                **self.config.node.attributes.entity(entity),
                **(self.config.node.defaults.unknown if key in tree.unknowns else {}),
                **(self.config.node.attributes.family(tree.families[key]) if key in tree.families else {}),
                **(self.config.node.attributes.member(entity.member) if entity.member is not None else {}),
                **self.config.node.attributes.by_key.get(key, {}),
            )
            for key, entity in tree.entities.items()
        ]

    def write_edges(self, tree: FamilyTree[AnyRank, M]) -> list[Edge]:
        return [
            Edge(
                parent_key,
                child_key,
                **(self.config.edge.defaults.unknown if parent_key in tree.unknowns else {}),
                **self.config.edge.attributes.by_key.get((parent_key, child_key), {}),
            )
            for (parent_key, child_key) in tree.relationships
        ]

    def write_cohort(self, rank: AnyRank, cohort: set[str]) -> Subgraph:
        return Subgraph(
            Attribute(rank="same"),
            Node(self.write_rank_identifier(self.config.graph.names.ranks_left, rank, "L")),
            Node(self.write_rank_identifier(self.config.graph.names.ranks_right, rank, "R")),
            *[Node(entity_id) for entity_id in sorted(cohort)],
        )

    def write_cohorts(self, cohorts: Optional[dict[AnyRank, set[str]]]) -> Optional[Subgraph]:
        return (
            Subgraph(
                self.config.graph.names.ranks,
                *[
                    self.write_cohort(
                        rank=rank,
                        cohort=cohort,
                    )
                    for rank, cohort in cohorts.items()
                ],
            )
            if cohorts is not None
            else None
        )
