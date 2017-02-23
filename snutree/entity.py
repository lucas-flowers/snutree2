from pprint import pformat
from abc import ABCMeta, abstractmethod
from . import SnutreeError
from .utilities import logged

@logged
def validate_members(member_list, member_types, ignored_statuses=None):

    ignored_statuses = ignored_statuses or []

    allowed_statuses = {}
    for typ in member_types:
        for allowed in typ.allowed:
            allowed_statuses[allowed] = typ

    members = []
    for member in member_list:

        # Remove the keys pointing to falsy values from each member. This
        # simplifies validation (e.g., we don't have to worry about
        # handling values of None or empty strings)
        for key, field in list(member.items()):
            if not field:
                del member[key]

        if len(allowed_statuses) == 1:
            # If there is only one type of member, ignore the status field
            #
            # TODO zero just takes the first one (it shouldn't matter, but
            # it's kind of ugly)
            status = next(iter(allowed_statuses.keys()))
        else:
            status = member.get('status')

        # Don't include if ignored
        if status in ignored_statuses:
            continue

        # Make sure the member status field is valid first
        if status not in allowed_statuses:
            msg = 'Invalid member status in:\n{}\nStatus must be one of:\n{}'
            vals = pformat(member), list(allowed_statuses.keys())
            raise DirectoryError(msg.format(*vals))

        # TODO error checking
        # TODO rename dict members and object members
        member = allowed_statuses[status].from_dict(member)
        members.append(member)

    return members

class TreeEntity(metaclass=ABCMeta):
    '''

    Analogous to a single row in the directory, except that the fields have
    been combined appropriately (i.e., first/preferred/last names combined into
    one field, or semester strings converted to Semester objects).

    Entities implement these functions:

        + dot_attributes(self): Returns the node attributes to be used in DOT

    Entities should also have these fields:

        + key: The key to be used in DOT

        + _semester: A private field storing a Semester object, used to
        determine the entity's rank in DOT

    '''

    @property
    def semester(self):
        if self._semester:
            return self._semester
        else:
            msg = 'missing semester value for entity {!r}'
            raise TreeEntityAttributeError(msg.format(self.key))

    @semester.setter
    def semester(self, value):
        self._semester = value

    def dot_attributes(self):
        return {}

class Custom(TreeEntity):

    def __init__(self, key, semester=None, attributes=None):
        self.key = key
        self.semester = semester
        self.attributes = attributes or {}

    def dot_attributes(self):
        return self.attributes

class UnidentifiedMember(Custom):
    '''
    All members are assumed to have big brothers. If a member does not have a
    known big brother, this class is used as a placeholder. UnidentifiedKnights
    are given pledge semesters a semester before the members they are bigs to,
    unless the semester is unknown in which case it is left null.
    '''

    def __init__(self, member, attributes=None):
        self.key = '{} Parent'.format(member.key)
        try:
            self.semester = member.semester - 1
        except TreeEntityAttributeError:
            self.semester = None
        self.attributes = attributes or {}

class Member(TreeEntity, metaclass=ABCMeta):
    '''
    A member of the organization. Every member provides these functions:

        + get_validator(cls): Returns a validator used to validate a row in the
        Directory that might contain this type of member.

        + get_dot_label(self): Returns the DOT label for the member, to be used
        in the member class's get_dot_attributes function.

    In addition, every member should have these fields:

        + parent: The (key of the) parent node of this member, i.e., the
        member's big brother.
    '''

    @classmethod
    @abstractmethod
    def from_dict(cls, dct):
        pass

    @abstractmethod
    def get_dot_label(self):
        pass

    def dot_attributes(self):
        return {'label' : self.get_dot_label()}

class DirectoryError(SnutreeError):
    pass

class TreeEntityAttributeError(SnutreeError):
    pass

