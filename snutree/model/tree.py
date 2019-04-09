
r'''

-----------------------------------
 cohort0  A      B       C       D
          |     / \     /|\      |
 cohort1  E    F  G    H I J     K
               |       |  / \    |
 cohort2       L       M N  O    P
-----------------------------------

'''

from dataclasses import dataclass, field
from typing import Sequence, Mapping

from networkx import DiGraph, weakly_connected_components

@dataclass(order=True)
class Entity:

    id: str
    classes: Sequence[str] = field(default_factory=list)
    data: Mapping = field(default_factory=dict)

    @classmethod
    def from_member(cls, member):
        return cls(
            id=member.key,
            classes=['root', 'tree'] + member.classes,
            data={'id': member.key}, # TODO ???
        )

@dataclass(order=True)
class Relationship:

    from_id: str
    to_id: str
    classes: Sequence[str] = field(default_factory=list)
    data: Mapping = field(default_factory=dict)

    @classmethod
    def from_member(cls, member):
        return cls(
            from_id=member.parent_key,
            to_id=member.id,
            classes=['root', 'tree'] + member.classes,
            data={'from_id': member.parent_key, 'to_id': member.key},
        )

@dataclass
class Cohort:

    rank: object
    ids: Sequence[str]
    classes: Sequence[str] = field(default_factory=list)
    data: Mapping = field(default_factory=dict)

    @property
    def id(self):
        # TODO Create an ID?
        return str(self.rank)

    @classmethod
    def from_members(cls, members, ranks):
        rank_to_ids = {rank: [] for rank in ranks}
        for member in members:
            rank_to_ids[member.rank].append(member.key)
        return [
            cls(
                rank=rank,
                ids=ids,
                classes=['root', 'rank'],
                data={'rank': rank}, # TODO ???
            ) for rank, ids in rank_to_ids.items()
        ]

class FamilyTree:

    def __init__(self, entities, relationships, cohorts=None, classes=None, data=None):

        self._entities = {
            entity.id: entity
            for entity in entities
        }
        self._relationships = {
            (relationship.from_id, relationship.to_id): relationship
            for relationship in relationships
        }

        # We don't /need/ to store a full graph; all the necessary information
        # is stored in entities and relationships. But this does make things
        # easier (and maybe faster?)
        self._graph = DiGraph()
        self._graph.add_nodes_from(self._entities.keys())
        self._graph.add_edges_from(self._relationships.keys())

        self.cohorts = cohorts
        self.classes = classes or []
        self.data = data or {}

    @property
    def entities(self):
        return self._entities.values()

    @property
    def relationships(self):
        return self._relationships.values()

    @property
    def families(self):
        return [
            [self._entities[entity_id] for entity_id in family_entity_ids]
            for family_entity_ids in weakly_connected_components(self._graph)
        ]

    @classmethod
    def from_members(cls, members, ranks=None):
        return cls(
            entities=list(map(Entity.from_member, members)),
            relationships=list(map(Relationship.from_member, members)),
            cohorts=Cohort.from_members(members, ranks) if ranks is not None else None,
            classes=['root'],
            data=None, # TODO ???
        )

