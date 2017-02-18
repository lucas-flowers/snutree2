import difflib, json
from ..entity import Member, Initiate
from ..utilities import nonempty_string, optional_nonempty_string, optional_semester_like

# TODO for SQL, make sure DA affiliations agree with the external ID.
# TODO sort affiliations in each member

greek_mapping = {
        'Alpha' : 'A',
        'Beta' : 'B',
        'Gamma' : 'Γ',
        'Delta' : 'Δ',
        'Epsilon' : 'E',
        'Zeta' : 'Z',
        'Eta' : 'H',
        'Theta' : 'Θ',
        'Iota' : 'I',
        'Kappa' : 'K',
        'Lambda' : 'Λ',
        'Mu' : 'M',
        'Nu' : 'N',
        'Xi' : 'Ξ',
        'Omicron' : 'O',
        'Pi' : 'Π',
        'Rho' : 'P',
        'Sigma' : 'Σ',
        'Tau' : 'T',
        'Upsilon' : 'Y',
        'Phi' : 'Φ',
        'Chi' : 'X',
        'Psi' : 'Ψ',
        'Omega' : 'Ω',
        '(A)' : '(A)', # Because of Eta Mu (A) Chapter
        '(B)' : '(B)', # Because of Eta Mu (B) Chapter
        }

def to_greek_name(english_name):
    try:
        return ''.join([greek_mapping[w] for w in english_name.split(' ')])
    except KeyError:
        msg = 'chapter names must be made of words in {}'
        val = sorted(greek_mapping.keys())
        raise ValueError(msg.format(val))

def coerce_affiliation(affiliation):
    vals = to_greek_name(affiliation['chapter_name']), affiliation['other_badge']
    return '{} {!s}'.format(*vals)

affiliations_schema = {
        'type' : 'list',
        'required' : False,
        'coerce' : lambda s : json.loads(s),
        'schema' : {
            'type' : 'string',
            'coerce' : coerce_affiliation
        }
    }

class Knight(Initiate):

    schema = {
            'status' : {'allowed' : ['Active', 'Alumni', 'Left School']},
            'badge' : nonempty_string,
            'first_name' : nonempty_string,
            'preferred_name' : optional_nonempty_string,
            'last_name' : nonempty_string,
            'big_badge' : optional_nonempty_string,
            'pledge_semester' : optional_semester_like,
            'affiliations' : affiliations_schema,
            }


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

        # TODO generalize
        self.affiliations = set(affiliations or []) | {'ΔA {}'.format(badge)}

    def get_key(self):
        return self.badge

    def get_dot_label(self):
        # TODO generalize
        affiliations =  sorted(self.affiliations, key=self.affiliations_key())
        return '{}\\n{}'.format(self.name, ', '.join(affiliations))

    def affiliations_key(self):
        # TODO generalize
        return lambda s : (not s.startswith('ΔA '), s)



class Brother(Member):

    schema = {
            'status' : {'allowed' : ['Brother']},
            'first_name' : optional_nonempty_string,
            'preferred_name' : optional_nonempty_string,
            'last_name' : nonempty_string,
            'big_badge' : optional_nonempty_string,
            'pledge_semester' : optional_semester_like,
            'affiliations' : {'allowed' : []}
            }

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

    schema = {
            'status' : {'allowed' : ['Candidate']},
            'first_name' : nonempty_string,
            'preferred_name' : optional_nonempty_string,
            'last_name' : nonempty_string,
            'big_badge' : optional_nonempty_string,
            'pledge_semester' : optional_semester_like,
            'affiliations' : {'allowed' : []}
            }

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
    '''
    A member that was initiated, but was then expelled.
    '''

    schema = {
            'status' : {'allowed' : ['Expelled']},
            'badge' : nonempty_string,
            'first_name' : optional_nonempty_string,
            'preferred_name' : optional_nonempty_string,
            'last_name' : optional_nonempty_string,
            'big_badge' : optional_nonempty_string,
            'pledge_semester' : optional_semester_like,
            'affiliations' : affiliations_schema
            }

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

