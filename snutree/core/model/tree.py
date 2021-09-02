import random
from dataclasses import dataclass
from functools import cached_property
from operator import index
from typing import Generic, Type, TypeVar

from networkx import DiGraph, weakly_connected_components

from snutree.core.model.common import Rank

AnyRank = TypeVar("AnyRank", bound=Rank)


class Cohort:
    pass


@dataclass
class Entity(Generic[AnyRank]):
    rank: AnyRank


@dataclass
class Relationship:
    pass


@dataclass
class Member(Entity[AnyRank]):
    pass


class Family:
    pass


@dataclass
class TreeConfig:

    rank_min_offset: int
    rank_max_offset: int

    def __post_init__(self) -> None:
        if self.rank_min_offset > 0:
            raise NotImplementedError("positive minimum rank offsets (i.e., entity filtering by rank) not implemented")
        if self.rank_max_offset < 0:
            raise NotImplementedError("negative maximum rank offsets (i.e., entity filtering by rank) not implemented")


class Tree(Generic[AnyRank]):  # pylint: disable=too-many-instance-attributes
    """
    A tree.
    """

    def __init__(
        self,
        rank_type: Type[AnyRank],
        entities: dict[str, Entity[AnyRank]],
        relationships: dict[tuple[str, str], Relationship],
        config: TreeConfig,
    ) -> None:

        self.rank_type = rank_type
        self.config = config

        self.entities = entities
        self.relationships = relationships

        self._digraph: DiGraph[str] = DiGraph()
        self._digraph.add_nodes_from(self.entities.keys())
        self._digraph.add_edges_from(self.relationships.keys())

        self._member_digraph = self._digraph.subgraph(
            entity_id for entity_id in self._digraph.nodes if isinstance(entities[entity_id], Member)
        )

        self._families: dict[str, Family] = {}
        self._family_roots: dict[Family, str] = {}
        for family_member_ids in weakly_connected_components(self._member_digraph):
            family = Family()
            (self._family_roots[family],) = set(
                family_member_id
                for family_member_id, degree in self._digraph.subgraph(family_member_ids).in_degree()
                if degree == 0
            )
            for family_member_id in family_member_ids:
                self._families[family_member_id] = family

    @cached_property
    def entity_ids(self) -> list[str]:
        """
        Return a list of entity_ids for this tree, sorted consistently.
        """
        components = sorted(weakly_connected_components(self._digraph), key=min)
        random.Random("12345").shuffle(components)  # TODO seed
        return [key for component in components for key in sorted(component)]

    @cached_property
    def relationship_ids(self) -> list[tuple[str, str]]:
        """
        Return a sorted list of relationship_ids (tuples of parent entity ID
        and child entity ID) for this tree.
        """
        return sorted(self._digraph.edges())

    @cached_property
    def cohorts(self) -> dict[Rank, set[str]]:
        """
        Return a mapping of ranks to their corresponding entity IDs.
        """

        unsorted_cohorts: dict[Rank, set[str]] = {}
        for entity_id, entity in self.entities.items():
            if entity.rank not in unsorted_cohorts:
                unsorted_cohorts[entity.rank] = set()
            unsorted_cohorts[entity.rank].add(entity_id)

        return {rank: unsorted_cohorts.get(rank) or set() for rank in self.ranks}

    @cached_property
    def ranks(self) -> list[AnyRank]:
        """
        Return a list of all the ranks of the tree, in order.
        """

        if len(self.entities) == 0:
            return []

        initial_rank = next(iter(self.entities.values())).rank
        min_rank, max_rank = initial_rank, initial_rank
        for entity in self.entities.values():
            if index(entity.rank) < index(min_rank):
                min_rank = entity.rank
            if index(entity.rank) > index(max_rank):
                max_rank = entity.rank

        return [
            self.rank_type(i)
            for i in range(
                index(min_rank) + self.config.rank_min_offset,
                index(max_rank) + self.config.rank_max_offset + 1,
            )
        ]
