
'''
Cleaned-up, Pythonic representation of a row. Input data structure for creating
a FamilyTree object.
'''

from dataclasses import dataclass, field

@dataclass
class Member:

    classes: list = field(default_factory=list)
    data: dict = field(default_factory=dict)

    @property
    def id(self):
        return self.data['id']

    @property
    def parent_id(self):
        return self.data['parent_id']

    @property
    def rank(self):
        return self.data['rank']

