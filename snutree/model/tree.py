import random
from collections.abc import Set
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from operator import index
from typing import (
    Generic,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
)

from networkx import DiGraph, weakly_connected_components
from networkx.algorithms.dag import descendants
from networkx.classes.function import freeze

from snutree.model.entity import (
    Entity,
    EntityId,
    ParentKeyStatus,
    UnknownEntity,
)
from snutree.model.rank import AnyRank

M = TypeVar("M")


class FamilyId(EntityId):
    pass


@dataclass
class FamilyTreeConfig:

    seed: int = 0
    include_unknowns: bool = True
    include_singletons: bool = False
    include_families: Optional[set[str]] = None

    unknown_offset: int = 1
    rank_min_offset: int = 0
    rank_max_offset: int = 0

    def __post_init__(self) -> None:
        if self.unknown_offset <= 0:
            raise ValueError("unknown member rank offsets must be strictly positive")
        if self.rank_min_offset > 0:
            raise NotImplementedError("positive minimum rank offsets (i.e., entity filtering by rank) not implemented")
        if self.rank_max_offset < 0:
            raise NotImplementedError("negative maximum rank offsets (i.e., entity filtering by rank) not implemented")


class FamilyTree(Generic[AnyRank, M]):
    """
    A tree.
    """

    def __init__(
        self,
        rank_type: Type[AnyRank],
        entities: Iterable[Entity[AnyRank, M]],
        relationships: set[tuple[EntityId, EntityId]],
        config: Optional[FamilyTreeConfig] = None,
    ) -> None:

        # TODO Verify identifiers
        # TODO Pass members directly?

        self.rank_type = rank_type
        self.config = config or FamilyTreeConfig()
        self._entities: Sequence[Entity[AnyRank, M]] = list(entities)
        self._relationships: Set[tuple[EntityId, EntityId]] = relationships

    @cached_property
    def lookup(self) -> Mapping[EntityId, Entity[AnyRank, M]]:
        """
        Return a non-ordered mapping of entity key to entity.
        """
        return {
            **{entity.key: entity for entity in self._entities},
            **{
                (
                    unknown_entity := UnknownEntity(
                        rank_type=self.rank_type,
                        child=entity,
                        offset=self.config.unknown_offset,
                    )
                ).key: unknown_entity
                for entity in self._entities
                if entity.parent_key == ParentKeyStatus.UNKNOWN
            },
        }

    @cached_property
    def graph(self) -> "DiGraph[EntityId]":
        """
        Return the networkx graph underlying this tree.
        """

        graph: DiGraph[EntityId] = DiGraph()

        # Add all entities with relationships, or that are known to have no
        # parents. These are always drawn on the tree unless rank filtering is
        # in place.
        graph.add_edges_from(self._relationships)
        for entity in self._entities:
            if entity.parent_key == ParentKeyStatus.NONE:
                graph.add_node(entity.key)
            elif entity.parent_key == ParentKeyStatus.UNKNOWN:
                pass
            else:
                assert isinstance(entity.parent_key, EntityId)
                graph.add_edge(entity.parent_key, entity.key)

        # Add all other entities (i.e., those without any relationships), if
        # this is desired.
        if self.config.include_singletons:
            graph.add_nodes_from(entity.key for entity in self._entities if entity.key not in graph)

        # If desired, keep only the families requested
        if self.config.include_families is not None:
            entity_ids = set(map(EntityId, self.config.include_families))
            entity_ids |= set(chain(*(descendants(graph, entity_id) for entity_id in entity_ids)))
            graph = DiGraph(graph.subgraph(entity_ids))

        # Add unknown parents entities if desired.
        if self.config.include_unknowns:
            for key, in_degree in list(graph.in_degree()):
                if self.lookup[key].parent_key == ParentKeyStatus.UNKNOWN and in_degree == 0:
                    parent_key = UnknownEntity.key_from(key)
                    graph.add_edge(parent_key, key)

        return freeze(graph)

    @cached_property
    def families(self) -> Mapping[EntityId, FamilyId]:
        """
        Return a dict of entity_id to the entity_id of the root of the entity's family.
        """

        member_graph = self.graph.subgraph(entity.key for entity in self._entities if entity.member is not None)

        families: dict[EntityId, FamilyId] = {}
        for family_member_ids in weakly_connected_components(member_graph):
            (root_member_id,) = set(
                family_member_id
                for family_member_id, degree in member_graph.subgraph(family_member_ids).in_degree()
                if degree == 0
            )
            for family_member_id in family_member_ids:
                families[family_member_id] = FamilyId(root_member_id)

        return families

    @cached_property
    def entities(self) -> Mapping[EntityId, Entity[AnyRank, M]]:
        """
        Return a dict of entity_ids for this tree, sorted consistently.
        """
        components = sorted(weakly_connected_components(self.graph), key=min)
        random.Random(self.config.seed).shuffle(components)
        return {key: self.lookup[key] for component in components for key in sorted(component)}

    @cached_property
    def relationships(self) -> Sequence[tuple[EntityId, EntityId]]:
        """
        Return a sorted list of relationship_ids (tuples of parent entity ID
        and child entity ID) for this tree.
        """
        return list(sorted(self.graph.edges()))

    @cached_property
    def cohorts(self) -> Mapping[AnyRank, Set[EntityId]]:
        """
        Return a mapping of ranks to their corresponding entity IDs.
        """

        unsorted_cohorts: dict[AnyRank, set[EntityId]] = {}
        for entity_id, entity in self.entities.items():
            if entity.rank not in unsorted_cohorts:
                unsorted_cohorts[entity.rank] = set()
            unsorted_cohorts[entity.rank].add(entity_id)

        return {rank: unsorted_cohorts.get(rank) or set() for rank in self.ranks}

    @cached_property
    def ranks(self) -> Sequence[AnyRank]:
        """
        Return a list of all the ranks of the tree, in order.
        """

        if len(self.entities) == 0:
            return []

        initial_rank = next(iter(self.entities.values())).rank
        min_rank, max_rank = initial_rank, initial_rank
        for entity in self.entities.values():
            rank = entity.rank
            if index(rank) < index(min_rank):
                min_rank = rank
            if index(rank) > index(max_rank):
                max_rank = rank

        return [
            self.rank_type(i)
            for i in range(
                index(min_rank) + self.config.rank_min_offset,
                index(max_rank) + self.config.rank_max_offset + 1,
            )
        ]
