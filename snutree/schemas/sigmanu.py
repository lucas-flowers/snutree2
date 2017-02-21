import difflib, re
from voluptuous import Schema, Optional, In, Coerce
from ..directory import Directory, DirectoryError
from ..entity import Member, Initiate
from ..semester import Semester
from ..utilities import NonEmptyString

# TODO for SQL, make sure DA affiliations agree with the external ID.
# TODO catch duplicate affiliations

# Voluptuous validators
AffiliationsList = lambda s : [Affiliation(a) for a in s.split(',')]

def directory(members):
    return SigmaNuDirectory(
            members,
            [Candidate, Brother, Knight, Expelled],
            ignored_statuses=['Reaffiliate']
            )

class SigmaNuDirectory(Directory):

    def set_members(self, members):

        def check_affiliations():
            '''
            A generator that iterates of the provided `members` iterable. Uses
            an excessively clever way to ensure all affiliations are unique.
            Depends on self._members[-1] containing the most-recently processed
            member.

            This /could/ be a method, but it is dependent on the innards of
            super().set_members and set_members is called only once per
            directory (in expected usage), so I'm leaving it as an inner
            function.
            '''

            used_affiliations = set()
            for m in members:
                yield m
                if m.get('status') not in self.ignored_statuses:
                    affiliations = self._members[-1].affiliations
                    for aff in affiliations:
                        if aff in used_affiliations:
                            msg = 'found duplicate affiliation: {!r}'
                            raise DirectoryError(msg.format(aff))
                        used_affiliations.add(aff)

        super().set_members(check_affiliations())

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
        self.affiliations = set(affiliations or []) | {Affiliation.with_primary(badge)}

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

        3. "Primary chapter": The chapter that will be listed first whenever
        Affiliations are sorted. This is assumed to be the chapter whose family
        tree is being generated.

    Thus, a chapter name might be "Delta Alpha" or "Eta Mu (A)". The
    corresponding chapter designations are "ΔA" and "ΗΜ(A)".

    '''

    # English words to Unicode Greek letters, in titlecaps
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

    def __init__(self, *args):
        '''
        Initialize a chapter affiliation based on args.

        If args is a string, it should be of the form '<chapter_id> <badge>'
        where <badge> is the badge number and <chapter_id> is an identifier for
        the chapter. That identifier can either be a chapter designation
        (essentially Greek letters with no spaces) or a full chapter name
        (English names of Greek letters, separated by spaces). In addition to
        Greek letters, the strings '(A)' and '(B)' are permissible for Eta Mu
        (A) and Eta Mu (B) chapters.

        If args is a tuple, it should be of length two and of the form
        "(<chapter_id>, <badge>)".
        '''

        if len(args) == 1 and isinstance(args[0], str):

            # Take out leading and trailing whitespace
            arg = args[0].strip()

            # Split into the name half and the digit half
            match = self.AFFILIATION_MATCHER.match(arg)
            if not match:
                msg = 'expected a chapter name followed by a badge number but got {!r}'
                raise ValueError(msg.format(arg))

            designation = self.str_to_designation(match.group('chapter_id'))
            badge = int(match.group('badge'))

        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            designation, badge = args

        else:
            msg = 'expected *(str,) or *(str, int) but got *{}'
            raise TypeError(msg.format(args))

        self.designation = designation
        self.badge = badge

    @classmethod
    def with_primary(cls, badge):
        '''
        Create an affiliation to the primary chapter with the given badge.
        '''

        # TODO make badge always an int, but replace the Member field with a
        # string key
        return cls(cls.get_primary_chapter(), int(badge))

    @classmethod
    def get_primary_chapter(cls):
        return cls._primary_chapter

    @classmethod
    def set_primary_chapter(cls, chapter_designation):
        cls._primary_chapter = cls.str_to_designation(chapter_designation)

    @classmethod
    def str_to_designation(cls, string):

        # See if string is a full chapter name (i.e., English words). Ignore
        # excessive whitespace and standardize to titlecaps before lookup.
        words = [w.title() for w in string.split()]
        greek_letters = [cls.ENGLISH_TO_GREEK[w] for w in words if w in cls.ENGLISH_TO_GREEK]
        if len(greek_letters) == len(words):
            designation = ''.join(greek_letters)

        # If the string's not a chapter name, then see if it's a short chapter
        # designation (i.e., Greek letters)
        elif cls.DESIGNATION_MATCHER.match(string):

            # Get a list of chapter designation tokens, capitalized
            tokens = re.findall(cls.DESIGNATION_TOKEN, string.upper())

            # Translate Latin lookalikes to true Greek
            greek_letters = [cls.LATIN_TO_GREEK.get(s, s) for s in tokens]

            designation = ''.join(greek_letters)

        else:
            msg = (
                    'expected a chapter name in one of the two forms:\n'
                    '    1. names of Greek letters separated by spaces (e.g., "Delta Alpha 100")\n'
                    '    2. several actual Greek letters together (e.g., "ΔA 100")\n'
                    'but got {!r}\n'
                    )
            raise ValueError(msg.format(string))

        return designation

    def __str__(self):
        return '{} {}'.format(self.designation, self.badge)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        '''
        Affiliations are sorted by chapter, then badge. The primary chapter
        always goes first.
        '''
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

