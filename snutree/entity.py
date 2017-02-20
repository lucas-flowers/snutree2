from abc import ABCMeta, abstractmethod

class TreeEntity(metaclass=ABCMeta):
    '''

    Analogous to a single row in the directory, except that the fields have
    been combined appropriately (i.e., first/preferred/last names combined into
    one field, or semester strings converted to Semester objects).

    Entities implement these functions:

        + get_key(self): Returns the key to be used in DOT

        + dot_attributes(self): Returns the node attributes to be used in DOT

    Entities should also have these fields:

        + _semester: A private field storing a Semester object, used to
        determine the entity's rank in DOT

    '''

    @abstractmethod
    def get_key(self):
        pass

    @property
    def semester(self):
        if self._semester:
            return self._semester
        else:
            msg = 'missing semester value for entity {!r}'
            raise TreeEntityAttributeError(msg.format(self.get_key()))

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

    def get_key(self):
        return self.key

    def dot_attributes(self):
        return self.attributes

class UnidentifiedInitiate(Custom):
    '''
    All members are assumed to have big brothers. If a member does not have a
    known big brother, this class is used as a placeholder. UnidentifiedKnights
    are given pledge semesters a semester before the members they are bigs to,
    unless the semester is unknown in which case it is left null.
    '''

    def __init__(self, member, attributes=None):
        self.key = '{} Parent'.format(member.get_key())
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
    def from_dict(cls, dct):
        return cls(**cls.validator(dct))

    @abstractmethod
    def get_dot_label(self):
        pass

    def dot_attributes(self):
        return {'label' : self.get_dot_label()}

class Initiate(Member, metaclass=ABCMeta):
    pass

class TreeEntityAttributeError(AttributeError):
    pass

