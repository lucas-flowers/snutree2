from abc import ABCMeta, abstractmethod
import difflib

class TreeEntity(metaclass=ABCMeta):
    '''

    Analogous to a single row in the directory, except that the fields have
    been combined appropriately (i.e., first/preferred/last names combined into
    one field, or semester strings converted to Semester objects).

    Entities implement these functions:

        + get_key(self): Returns the key to be used in DOT

        + dot_attributes(self): Returns the node attributes to be used in DOT

    Entities should also have these fields:

        + semester: A field storing a Semester object, used to determine the
        entity's rank in DOT

    '''

    @abstractmethod
    def get_key(self):
        pass

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

class UnidentifiedKnight(Custom):
    '''
    All members are assumed to have big brothers. If a member does not have a
    known big brother, this class is used as a placeholder. UnidentifiedKnights
    are given pledge semesters a semester before the members they are bigs to.
    '''

    def __init__(self, member, attributes=None):
        self.key = member.get_key()
        self.semester = member.semester - 1
        self.attributes = attributes or {}

    def get_key(self):
        return '{} Parent'.format(self.key)

class Member(TreeEntity, metaclass=ABCMeta):

    @abstractmethod
    def get_dot_label(self):
        pass

    def dot_attributes(self):
        return {'label' : self.get_dot_label()}

class KeylessEntity(Member):

    def __init__(self, status=None, name=None, pledge_semester=None, big_name=None):

        self.key = name
        self.semester = pledge_semester
        self.parent = big_name

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return self.key

class Knight(Member):

    def __init__(self,
            status=None,
            badge=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            ):

        self.badge = badge
        self.name = combine_names(first_name, preferred_name, last_name)
        self.parent = big_badge
        self.semester = pledge_semester
        self.affiliations = []

    def get_key(self):
        return self.badge

    def get_dot_label(self):
        affiliations = ['ΔA {}'.format(self.badge)] + self.affiliations
        return '{}\\n{}'.format(self.name, ', '.join(affiliations))

class Brother(Member):

    bid = 0

    def __init__(self,
            status=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            ):

        self.name = last_name
        self.parent = big_badge
        self.semester = pledge_semester
        self.affiliations = []

        # Brothers who are not Knights do not have badge numbers; use a simple
        # counter to generate keys.
        self.key = 'Brother {}'.format(Brother.bid)
        Brother.bid += 1

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return '{}\\nΔA Brother'.format(self.name)

class Candidate(Member):

    cid = 0

    def __init__(self,
            status=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            ):

        self.name = combine_names(first_name, preferred_name, last_name)
        self.parent = big_badge
        self.semester = pledge_semester
        self.affiliations = []

        # Candidates do not have badge numbers; use a simple counter to
        # generate keys.
        self.key = 'Candidate {}'.format(Candidate.cid)
        Candidate.cid += 1

    def get_key(self):
        return self.key

    def get_dot_label(self):
        return '{}\\nΔA Candidate'.format(self.name)

class Expelled(Knight):

    def __init__(self,
            status=None,
            badge=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            ):

        self.badge = badge
        self.name = 'Member Expelled'
        self.parent = big_badge
        self.semester = pledge_semester
        self.affiliations = []

    def get_dot_label(self):
        return '{}\\n{}'.format(self.name, self.badge)

def combine_names(first_name, preferred_name, last_name, threshold=.5):
    '''
    Returns
    =======

    + Either: "[preferred] [last]" if the `preferred` is not too similar to
    `last`, depending on the threshold

    + Or: "[first] [last]" if `preferred` is too similar to `last`

    Notes
    =====

    This might provide a marginally incorrect name for those who
       a. go by something other than their first name that
       b. is similar to their last name,
    but otherwise it should almost always[^note] provide something reasonable.

    The whole point here is to
       a. avoid using *only* last names on the tree, while
       b. using the "first" names brothers actually go by, and while
       c. avoiding using a first name that is a variant of the last name.

    [^note]: I say "almost always" because, for example, someone with the
    last name "Richards" who goes by "Dick" will be listed incorrectly as "Dick
    Richards" even if his other names are neither Dick nor Richard (unless the
    tolerance threshold is made very low).
    '''

    if preferred_name and difflib.SequenceMatcher(None, preferred_name, last_name).ratio() < threshold:
        first_name = preferred_name

    return '{} {}'.format(first_name, last_name)

