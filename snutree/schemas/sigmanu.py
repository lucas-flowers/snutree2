import difflib, re
from functools import total_ordering
from voluptuous import Schema, Optional, All, Length, In, Coerce
from ..entity import Member, Initiate
from ..semester import Semester

# TODO for SQL, make sure DA affiliations agree with the external ID.

@total_ordering
class Affiliation:
    '''
    A chapter affiliation. Two definitions should be made clear here:

        1. "Chapter designation": A string of tokens, with no spaces between
        them. The allowed tokens are the following:

            + Upper- and lowercase Greek letters like Α, Σ, and π

            + Latin letters that look like Greek letters, like A and H

            + The strings '(A)' and '(B)', which are used to represent the
            chapters HM(A) and HM(B)

        2. "Chapter name": A string of words separated by whitespace. The
        allowed words are '(A)', '(B)', and the English names of any Greek
        letter. They are case-insensitive.

    '''

    @classmethod
    def get_primary_chapter(cls):
        return cls._primary_chapter

    @classmethod
    def set_primary_chapter(cls, chapter_designation):
        cls._primary_chapter = cls.str_to_designation(chapter_designation)

    # English words to Unicode Greek letters
    ENGLISH_TO_GREEK = {
            'Alpha' :'Α',
            'Beta' :'Β',
            'Gamma' :'Γ',
            'Delta' :'Δ',
            'Epsilon' :'Ε',
            'Zeta' :'Ζ',
            'Eta' :'Η',
            'Theta' :'Θ',
            'Iota' :'Ι',
            'Kappa' :'Κ',
            'Lambda' :'Λ',
            'Mu' :'Μ',
            'Nu' :'Ν',
            'Xi' :'Ξ',
            'Omicron' :'Ο',
            'Pi' :'Π',
            'Rho' :'Ρ',
            'Sigma' :'Σ',
            'Tau' :'Τ',
            'Upsilon' :'Υ',
            'Phi' :'Φ',
            'Chi' :'Χ',
            'Psi' :'Ψ',
            'Omega' :'Ω',
            '(A)' : '(A)', # Because of Eta Mu (A) Chapter
            '(B)' : '(B)', # Because of Eta Mu (B) Chapter
            }

    # Latin letters that look like the Unicode Greek letters they are keys for.
    # Note how they are all capital letters.
    LATIN_TO_GREEK = {
            # Latin : Greek
            'A' : 'Α',
            'B' : 'Β',
            'E' : 'Ε',
            'Z' : 'Ζ',
            'H' : 'Η',
            'I' : 'Ι',
            'K' : 'Κ',
            'M' : 'Μ',
            'N' : 'Ν',
            'O' : 'Ο',
            'P' : 'Ρ',
            'T' : 'Τ',
            'Y' : 'Υ',
            'X' : 'Χ',
            '(A)' : '(A)', # Because of Eta Mu (A) Chapter
            '(B)' : '(B)', # Because of Eta Mu (B) Chapter
            }

    # Initial matcher for affiliations (something, then spaces, then a badge)
    AFFILIATION_MATCHER = re.compile('(?P<chapter_id>.*)\s+(?P<badge>\d+)')

    # Valid tokens for chapter designations
    DESIGNATION_TOKENS = set.union(

            # Capital Greek letters, plus '(A)' and '(B)'
            set(ENGLISH_TO_GREEK.values()),

            # Lowercase Greek letters, plus '(a)' and '(b)'
            {c.lower() for c in ENGLISH_TO_GREEK.values()},

            # Alternative lowercase sigma
            {'ς'},

            # Latin letters that look like Greek letters
            set(LATIN_TO_GREEK.keys()),

            )

    # A pattern for matching a single chapter designation token
    DESIGNATION_TOKEN = '|'.join([re.escape(s) for s in DESIGNATION_TOKENS])

    # Matches a chapter designation
    DESIGNATION_MATCHER = re.compile('^({})+$'.format(DESIGNATION_TOKEN))

    def __init__(self, arg):
        '''
        Initialize a chapter affiliation based on arg, which should be a string
        of the form '<chapter_id> <badge>' where <badge> is the badge number
        and <chapter_id> is an identifier for the chapter. That identifier can
        either be a chapter designation (essentially Greek letters with no
        spaces) or a full chapter name (English names of Greek letters,
        separated by spaces). In addition to Greek letters, the strings '(A)'
        and '(B)' are permissible for Eta Mu (A) and Eta Mu (B) chapters.
        '''

        if not isinstance(arg, str):
            raise TypeError('expected str')

        # Take out leading and trailing whitespace
        arg = arg.strip()

        # Split into the name half and the digit half
        match = self.AFFILIATION_MATCHER.match(arg)
        if not match:
            msg = 'expected a chapter name followed by a badge number but got {!r}'
            raise ValueError(msg.format(arg))

        self.designation = self.str_to_designation(match.group('chapter_id'))
        self.badge = int(match.group('badge'))

    @classmethod
    def str_to_designation(cls, string):

        # See if string is a full chapter name (i.e., English words)
        words = [w.title() for w in string.split()]
        greek_letters = [cls.ENGLISH_TO_GREEK[w] for w in words if w in cls.ENGLISH_TO_GREEK]
        if len(greek_letters) == len(words):
            designation = ''.join(greek_letters)

        # See if string is a short chapter designation (i.e., Greek letters)
        elif cls.DESIGNATION_MATCHER.match(string):

            # Get a list of chapter designation tokens, capitalized
            tokens = re.findall(cls.DESIGNATION_TOKEN, string.upper())

            # Translate Latin lookalikes to true Greek
            greek_letters = [cls.LATIN_TO_GREEK.get(s, s) for s in tokens]

            designation = ''.join(greek_letters)

        else:
            msg = 'expected a chapter name in one of the two forms:\n' \
                    '    1. names of Greek letters separated by spaces (e.g., "Delta Alpha 100")\n' \
                    '    2. several actual Greek letters together (e.g., "ΔA 100")\n' \
                    'but got {!r}'
            raise ValueError(msg.format(string))

        return designation

    def __str__(self):
        return '{} {}'.format(self.designation, self.badge)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        if not isinstance(other, Affiliation):
            return NotImplemented
        key_self = (self.designation != self._primary_chapter, self.designation, self.badge)
        key_other = (other.designation != self._primary_chapter, other.designation, other.badge)
        return  key_self < key_other

    def __eq__(self, other):
        return isinstance(other, Affiliation) and \
                (self.designation, self.badge) == (other.designation, other.badge)

    def __hash__(self):
        return hash((self.designation, self.badge))

# TODO generalize
Affiliation.set_primary_chapter('ΔA')

NonEmptyString = All(str, Length(min=1))

AffiliationsList = lambda s : [Affiliation(a) for a in s.split(',')]

class Knight(Initiate):

    allowed = {'Active', 'Alumni', 'Left School'}

    validator = Schema({
        'status' : In(allowed),
        'badge' : NonEmptyString,
        'first_name' : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        'last_name' : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : Coerce(Semester),
        Optional('affiliations') : AffiliationsList,
        })

    def __init__(self,
            status=None,
            badge=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            affiliations=None,
            ):

        self.badge = badge
        self.name = combine_names(first_name, preferred_name, last_name)
        self.parent = big_badge
        self.semester = pledge_semester

        self.affiliations = set(affiliations or []) |  \
                {Affiliation('{} {}'.format(Affiliation.get_primary_chapter(), badge))}

    def get_key(self):
        return self.badge

    def get_dot_label(self):
        affiliation_strings =  [str(s) for s in sorted(self.affiliations)]
        return '{}\\n{}'.format(self.name, ', '.join(affiliation_strings))

class Brother(Member):

    allowed = {'Brother'}

    validator = Schema({
        'status' : In(allowed),
        Optional('first_name') : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        'last_name' : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : Coerce(Semester),
        Optional('affiliations') : AffiliationsList,
        })

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
        template = '{}\\n{} Brother'
        values = self.name, Affiliation.get_primary_chapter()
        return template.format(*values)

class Candidate(Member):

    allowed = {'Candidate'}

    validator = Schema({
        'status' : In(allowed),
        'first_name' : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        'last_name' : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : Coerce(Semester),
        Optional('affiliations') : AffiliationsList,
        })

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
        template = '{}\\n{} Candidate'
        values = self.name, Affiliation.get_primary_chapter()
        return template.format(*values)

class Expelled(Knight):
    '''
    A member that was initiated, but was then expelled.
    '''

    allowed = {'Expelled'}

    validator = Schema({
        'status' : In(allowed),
        'badge' : NonEmptyString,
        Optional('first_name') : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        Optional('last_name') : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : Coerce(Semester),
        Optional('affiliations') : AffiliationsList,
        })

    def __init__(self,
            status=None,
            badge=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            affiliations=None
            ):

        self.badge = badge
        self.name = 'Member Expelled'
        self.parent = big_badge
        self.semester = pledge_semester
        self.affiliations = affiliations or []

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

