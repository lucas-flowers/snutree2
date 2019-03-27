
'''
-----------------------------------
 cohort0  A      B       C       D
          |     / \     /|\      |
 cohort1  E    F  G    H I J     K
               |       |  / \    |
 cohort2       L       M N  O    P
-----------------------------------
'''

from typing import NamedTuple, List

class Entity(NamedTuple):

    id: str
    classes: List[str]
    data: dict

    @classmethod
    def from_member(cls, member):
        return cls(
            id=member.key,
            classes=member.classes, # TODO ???????
            data={'id': member.key}, # TODO ???
        )

class Relationship(NamedTuple):

    from_id: str
    to_id: str
    classes: List[str]
    data: dict

    @classmethod
    def from_member(cls, member):
        return cls(
            from_id=member.parent_key,
            to_id=member.id,
            classes=None, # TODO ?????
            data={'from_id': member.parent_key, 'to_id': member.key},
        )

class Cohort(NamedTuple):

    rank: object
    ids: List[str]
    classes: List[str]
    data: dict

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
                classes=None, # TODO ???
                data={'rank': rank}, # TODO ???
            ) for rank, ids in rank_to_ids.items()
        ]

class FamilyTree(NamedTuple):

    entities: List[Entity]
    relationships: List[Relationship]
    cohorts: List[Cohort] # Or None
    classes: List[str]
    data: dict

    @classmethod
    def from_members(members, ranks=None):
        return FamilyTree(
            entities=list(map(Entity.from_member, members)),
            relationships=list(map(Relationship.from_member, members)),
            cohorts=Cohort.from_members(members, ranks) if ranks is not None else None,
            classes=None, # TODO ???
            data=None, # TODO ???
        )

