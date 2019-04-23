
from .model import Entity, Relationship, Cohort, FamilyTree

def create(members, config=None):
    factory = TreeFactory(config or {})
    ranks = [member.rank for member in members]
    rank_range = range(min(ranks), max(ranks)+1)
    return factory.family_tree(members, rank_range)

class TreeFactory:

    def __init__(self, config):
        self.config = config

    def entity(self, member):
        return Entity(
            id=member.id,
            classes=['root', 'tree'] + member.classes, # TODO ???
            data=member.data,
        )

    def relationship(self, member):
        return Relationship(
            from_id=member.parent_id,
            to_id=member.id,
            classes=['root', 'tree'], # TODO???
            data=member.data,
        )

    def relationships(self, members):
        return [
            self.relationship(member)
            for member in members
            if member.parent_id # TODO is not None
        ]

    def cohorts(self, members, ranks):
        rank_to_ids = {rank: [] for rank in ranks}
        for member in members:
            rank_to_ids[member.rank].append(member.id)
        return [
            Cohort(
                rank=rank,
                ids=ids,
                classes=['root', 'rank'], # TODO???
                data={'rank': rank}, # TODO???
            )
            for rank, ids in rank_to_ids.items()
        ]

    def family_tree(self, members, ranks=None):
        return FamilyTree(
            entities=list(map(self.entity, members)),
            relationships=self.relationships(members),
            cohorts=self.cohorts(members, ranks) if ranks is not None else None,
            classes=['root'], # TODO ???
            data={}, # TODO???
        )


