
from dataclasses import dataclass

@dataclass
class Member:

    classes: list
    data: dict

    @property
    def id(self):
        return self.data['id']

    @property
    def parent_id(self):
        return self.data['parent_id']

    @property
    def rank(self):
        return self.data['rank']

