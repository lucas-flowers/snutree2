
'''
Cleaned-up, Pythonic representation of a row. Input data structure for creating
a FamilyTree object.
'''

from dataclasses import dataclass, field

@dataclass
class Member:
    id: str
    parent_id: str
    rank: object
    classes: list = field(default_factory=list)
    data: dict = field(default_factory=dict)

