import random
from dataclasses import dataclass
from functools import cached_property
from typing import Generic, Optional, TypeVar, Union

from networkx import DiGraph, weakly_connected_components

from snutree.core.model.common import Rank

OptionalAnyRank = TypeVar("OptionalAnyRank", bound=Union[Rank, None])

T = TypeVar("T")


class Cohort:
    pass


@dataclass
class Component:
    classes: list[str]
    data: dict[str, str]


@dataclass
class CustomEntity(Component):
    rank: Rank


@dataclass
class CustomRelationship(Component):
    pass


@dataclass
class Member(Component):
    rank: Rank
    parent_id: str


Entity = Union[Member, CustomEntity]


class Family:
    pass


# Probably gonna need tobe Generic[T, R], one for member, one for rank
class Tree(Generic[T]):
    """
    A tree.
    """

    # _entities: dict[str, Entity]
    # _relationships: dict[tuple[str, str], Relationship]
    # cohorts: Optional[dict[Rank, list[str]]]

    def __init__(
        self,
        members: dict[str, Member],
        custom_entities: dict[str, CustomEntity],
        custom_relationships: dict[tuple[str, str], CustomRelationship],
    ) -> None:

        self.members = members
        self.custom_entities = custom_entities
        self.custom_relationships = custom_relationships

        self._digraph = DiGraph[str]()

        self._digraph.add_nodes_from(self.members.keys())
        self._digraph.add_edges_from((member.parent_id, child_id) for child_id, member in self.members.items())

        self._digraph.add_nodes_from(custom_entities.keys())
        self._digraph.add_edges_from(custom_relationships.keys())

        self._member_digraph = self._digraph.subgraph(
            entity_id for entity_id in self._digraph.nodes if entity_id in self.members
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
    def cohorts(self) -> Optional[dict[Rank, list[str]]]:
        """
        Return a mapping of ranks to their corresponding entity IDs.

        Return None if the tree is rankless.
        """
        ...

    @cached_property
    def ranks(self) -> Optional[list[Rank]]:
        """
        Return a list of all the ranks of the tree, in order.

        Return None if the tree is rankless.
        """
