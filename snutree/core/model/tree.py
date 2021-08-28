from dataclasses import dataclass
from typing import Generic

from snutree.core.model.common import AnyRank, Component


class Entity(Component, Generic[AnyRank]):
    cohort: AnyRank


class Relationship(Component):
    pass


@dataclass
class FamilyTree(Component, Generic[AnyRank]):
    entities: dict[str, Entity[AnyRank]]
    relationships: dict[tuple[str, str], Relationship]
