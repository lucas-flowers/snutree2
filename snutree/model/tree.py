import random
from collections.abc import Set
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from operator import index
from typing import (
    Generic,
    Iterable,
    Literal,
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
class FamilyTreeConfig(Generic[AnyRank]):  # pylint: disable=too-many-instance-attributes

    seed: int = 0
    include_unknowns: bool = True
    include_singletons: bool = False
    include_families: Optional[set[str]] = None

    unknown_offset: int = 1

    rank_min: Optional[AnyRank] = None
    rank_min_offset: int = 0

    rank_max: Optional[AnyRank] = None
    rank_max_offset: int = 0

    def __post_init__(self) -> None:
        if self.unknown_offset <= 0:
            raise ValueError("unknown member rank offsets must be strictly positive")
        if self.rank_min_offset > 0:
            raise ValueError("positive minimum rank offsets not implemented")
        if self.rank_max_offset < 0:
            raise ValueError("negative maximum rank offsets not implemented")
        if self.rank_min is not None and self.rank_max is not None:
            if index(self.rank_min) > index(self.rank_max):
                raise ValueError("min rank must be less than or equal to max rank")


class FamilyTree(Generic[AnyRank, M]):
    """
    A tree.
    """

    def __init__(
        self,
        rank_type: Type[AnyRank],
        entities: Iterable[Entity[AnyRank, M]],
        relationships: set[tuple[EntityId, EntityId]],
        config: Optional[FamilyTreeConfig[AnyRank]] = None,
    ) -> None:

        # TODO Verify identifiers
        # TODO Pass members directly?

        self.rank_type = rank_type
        self.config = config or FamilyTreeConfig()

        min_rank = float("-inf") if self.config.rank_min is None else index(self.config.rank_min)
        max_rank = index(self.config.rank_max) if self.config.rank_max is not None else float("inf")
        self._entities: Sequence[Entity[AnyRank, M]] = [
            entity for entity in entities if min_rank <= index(entity.rank) <= max_rank
        ]

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
    def core(self) -> "DiGraph[EntityId]":
        """
        Return the graph containing all entities that have relationships, or
        that are *known* to have no relationships. These entities are always
        drawn on the tree.
        """

        graph: DiGraph[EntityId] = DiGraph()

        graph.add_edges_from(self._relationships)
        for entity in self._entities:
            if entity.parent_key == ParentKeyStatus.NONE:
                graph.add_node(entity.key)
            elif entity.parent_key == ParentKeyStatus.UNKNOWN:
                pass
            else:
                assert isinstance(entity.parent_key, EntityId)
                graph.add_edge(entity.parent_key, entity.key)

        return graph

    @cached_property
    def singletons(self) -> set[EntityId]:
        """
        Return all entities that have no known parents.
        """
        return {entity.key for entity in self._entities if entity.key not in self.core}

    @cached_property
    def graph(self) -> "DiGraph[EntityId]":
        """
        Return the networkx graph underlying this tree.
        """

        graph: DiGraph[EntityId] = DiGraph(self.core)

        if self.config.include_singletons:
            graph.add_nodes_from(self.singletons)

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

        rng = random.Random(self.config.seed)
        components = sorted(weakly_connected_components(self.graph), key=min)
        rng.shuffle(components)

        entities: dict[EntityId, Entity[AnyRank, M]] = {}
        for component in components:
            entity_ids: list[EntityId] = list(sorted(component))
            rng.shuffle(entity_ids)
            for key in entity_ids:
                entities[key] = self.lookup[key]

        return entities

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
    def max_rank(self) -> Optional[AnyRank]:
        return self.bound(sign=1)

    @cached_property
    def min_rank(self) -> Optional[AnyRank]:
        return self.bound(sign=-1)

    def bound(self, *, sign: Literal[-1, 1]) -> Optional[AnyRank]:
        """
        Return the maximum rank to be included, plus the configured rank offset.

        Return None if there are no ranks.
        """

        if sign > 0:
            max_configured = self.config.rank_max
            offset = self.config.rank_max_offset
        else:
            max_configured = self.config.rank_min
            offset = self.config.rank_min_offset

        max_used: Optional[AnyRank] = None
        for key in self.graph:
            entity = self.lookup[key]
            if max_used is None or sign * index(entity.rank) > sign * index(max_used):
                max_used = entity.rank

        if max_used is None:
            bound = self.config.rank_max
        elif max_configured is None:
            bound = max_used
        else:
            bound = self.rank_type(
                sign
                * min(
                    sign * index(max_configured),
                    sign * index(max_used),
                )
            )

        if bound is None:
            return None
        else:
            return self.rank_type(index(bound) + offset)

    @cached_property
    def ranks(self) -> Sequence[AnyRank]:
        """
        Return a list of all the ranks of the tree, in order.
        """
        if self.min_rank is None and self.max_rank is None:
            return []
        elif self.min_rank is not None and self.max_rank is None:
            return [self.min_rank]
        elif self.min_rank is None and self.max_rank is not None:
            return [self.max_rank]
        else:
            return [
                self.rank_type(i)
                for i in range(
                    index(self.min_rank),
                    index(self.max_rank) + 1,
                )
            ]
