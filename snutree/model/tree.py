import random
from dataclasses import dataclass
from functools import cached_property
from operator import index
from typing import (
    Generic,
    Iterable,
    Optional,
    Protocol,
    Type,
    TypeVar,
    runtime_checkable,
)

from networkx import DiGraph, weakly_connected_components

AnyRank = TypeVar("AnyRank", bound="Rank")
AnyRank_co = TypeVar("AnyRank_co", bound="Rank", covariant=True)


M = TypeVar("M")


@runtime_checkable
class Rank(Protocol):
    def __init__(self, i: Optional[int] = None, /) -> None:  # pylint: disable=super-init-not-called
        ...

    def __index__(self) -> int:  # pylint: disable=invalid-index-returned # Come on pylint, it's a protocol
        ...


@dataclass
class Entity(Generic[AnyRank, M]):
    parent_key: Optional[str]
    key: str
    rank: AnyRank
    member: Optional[M]


@dataclass
class FamilyTreeConfig:

    seed: str = "12345"
    rank_min_offset: int = 0
    rank_max_offset: int = 0

    def __post_init__(self) -> None:
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
        relationships: set[tuple[str, str]],
        config: Optional[FamilyTreeConfig] = None,
    ) -> None:

        # TODO Verify identifiers
        # TODO Pass members directly?

        self.rank_type = rank_type
        self.config = config or FamilyTreeConfig()

        self._entities: dict[str, Entity[AnyRank, M]] = {}
        self._relationships = relationships
        for entity in entities:
            self._entities[entity.key] = entity
            if entity.parent_key is not None:
                self._relationships.add((entity.parent_key, entity.key))

        self._digraph: DiGraph[str] = DiGraph()
        self._digraph.add_nodes_from(self._entities.keys())
        self._digraph.add_edges_from(self._relationships)

        self._member_digraph = self._digraph.subgraph(
            entity.key for entity in self._entities.values() if entity.member is not None
        )

    @cached_property
    def families(self) -> dict[str, str]:
        """
        Return a dict of entity_id to the entity_id of the root of the entity's family.
        """
        families: dict[str, str] = {}
        for family_member_ids in weakly_connected_components(self._member_digraph):
            (root_member_id,) = set(
                family_member_id
                for family_member_id, degree in self._member_digraph.subgraph(family_member_ids).in_degree()
                if degree == 0
            )
            for family_member_id in family_member_ids:
                families[family_member_id] = root_member_id
        return families

    @cached_property
    def entities(self) -> dict[str, Entity[AnyRank, M]]:
        """
        Return a dict of entity_ids for this tree, sorted consistently.
        """
        components = sorted(weakly_connected_components(self._digraph), key=min)
        random.Random(self.config.seed).shuffle(components)
        return {key: self._entities[key] for component in components for key in sorted(component)}

    @cached_property
    def relationships(self) -> list[tuple[str, str]]:
        """
        Return a sorted list of relationship_ids (tuples of parent entity ID
        and child entity ID) for this tree.
        """
        return list(sorted(self._digraph.edges()))

    @cached_property
    def cohorts(self) -> dict[AnyRank, set[str]]:
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

        if len(self._entities) == 0:
            return []

        initial_rank = next(iter(self._entities.values())).rank
        min_rank, max_rank = initial_rank, initial_rank
        for entity in self._entities.values():
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
