
'''
Cleaned-up, Pythonic representation of a row. Input data structure for creating
a FamilyTree object.
'''

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Member:
    '''
    Represent a member. Note these non-constraints:

        + Members might have null identifiers (although this would make it
        impossible to assign children to the member)

        + Members might have null parent identifiers (the member might be a
        root, or the member's parent might be unknown)

        + Ranks are optional
    '''

    id: Optional[str]
    parent_id: Optional[str]
    rank: Optional[object]
    classes: list = field(default_factory=list)
    data: dict = field(default_factory=dict)

@dataclass
class ExtendedMember:
    '''
    Very similar to a Member, except extended to satisfy these constraints:

        + Every ExtendedMember has a non-null identifier

        + The only ExtendedMembers with null identifiers are members who truly
        have no parent (as opposed to having an unknown parent), i.e., roots

        + Ranks are still optional
    '''
    id: str
    parent_id: Optional[str]
    has_unknown_parent: bool
    rank: Optional[object]
    classes: list = field(default_factory=list)
    data: dict = field(default_factory=dict)

