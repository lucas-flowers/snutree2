from collections import defaultdict
from voluptuous.humanize import validate_with_humanized_errors as validate
from voluptuous import Invalid, Required, Schema, All, Any, Length, Optional, Unique
from family_tree.entity import Knight, Brother, Candidate, Expelled, KeylessInitiate
from family_tree.semester import Semester

###############################################################################
###############################################################################
#### Schema Utilities                                                      ####
###############################################################################
###############################################################################

# Matches nonempty strings
NonEmptyString = All(str, Length(min=1), msg='must be a nonempty string')

# Matches member types according to the dict, and returns the right constructor
def MemberType(status_string):
    member_status_mapping = {
            'Knight' : Knight,
            'Brother' : Brother,
            'Candidate' : Candidate,
            'Expelled' : Expelled,
            'KeylessInitiate' : KeylessInitiate,
            }
    member_type = member_status_mapping[status_string]
    def validator(string):
        if string == status_string:
            return member_type
        else:
            raise Invalid('status must be one of {{{}}}'.format(', '.join(member_status_mapping.keys())))
    return validator

# Semesters or strings that can be converted to semesters
def SemesterLike(semester_string):
    try:
        return Semester(semester_string)
    except (TypeError, ValueError) as e:
        raise Invalid(str(e))

###############################################################################
###############################################################################
#### Directory                                                             ####
###############################################################################
###############################################################################

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

class Directory:
    '''
    This class is used to store data from either a CSV file or a SQL query. It
    is an intermediate form before the data is turned into a tree. It stores a
    list of brothers from the directory, a list for brothers not made knights,
    a dictionary of affiliations, and a dictionary of YAML settings.

    The Directory class guarantees that entries in its members and affiliations
    lists will be dictionaries that follow the following schema.

    Furthermore, the class guarantees that all members in the member list are
    unique (as determined by their badge), and that all
    chapter_name/other_badge pairs in the affiliations list are unique.
    '''

    # The schema for the two tables (members and affiliations) are lists of
    # dictionaries, which cerberus appears not to be focused on because
    # cerberous is focused on nested dictionaries. I tried a cerberus schema
    # here, but it was very slow (possibly my fault). It's just simpler to use
    # voluptuous here.

    member_schema = Schema(Any(

        {
            Required('status') : MemberType('KeylessInitiate'),
            Required('name') : NonEmptyString,
            Optional('big_name') : Any(None, NonEmptyString),
            Optional('pledge_semester') : SemesterLike,
            },

        {
            Required('status') : MemberType('Knight'),
            Required('badge') : NonEmptyString,
            Required('first_name') : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            Required('last_name') : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : SemesterLike,
            },

        {
            Required('status') : MemberType('Brother'),
            Optional('first_name') : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            Required('last_name') : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : SemesterLike,
            },

        {
            Required('status') : MemberType('Candidate'),
            Required('first_name') : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            Required('last_name') : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : SemesterLike,
            },

        {
            Required('status') : MemberType('Expelled'),
            Required('badge') : NonEmptyString,
            Optional('first_name') : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            Optional('last_name') : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : SemesterLike,
            },

        ), required=True, extra=False)

    affiliations_schema = Schema({
        Required('badge') : NonEmptyString,
        Required('chapter_name') : NonEmptyString,
        Required('other_badge') : NonEmptyString,
        })

    def __init__(self, member_list, affiliations_list, settings_dict):

        self.settings = settings_dict
        self.set_members(member_list)
        self.mark_affiliations(affiliations_list)

    def set_members(self, members):

        members = [validate(m, self.member_schema) for m in members]
        validate([m['badge'] for m in members if 'badge' in m], Schema(Unique()))

        self._members = []
        for row in members:
            MemberType = row['status']
            self._members.append(MemberType(**row))

    def mark_affiliations(self, affiliations):

        affiliations = [validate(a, self.affiliations_schema) for a in affiliations]
        validate([(a['chapter_name'], a['other_badge']) for a in affiliations], Schema(Unique()))

        affiliations_map = defaultdict(list)
        for row in affiliations:
            badge = row['badge']
            other_badge = '{} {}'.format(to_greek_name(row['chapter_name']), row['other_badge'])
            affiliations_map[badge].append(other_badge)

        for member in self._members:
            member.affiliations = affiliations_map[member.get_key()]

    def get_members(self):
        return self._members

def to_greek_name(english_name):
    return ''.join([greek_mapping[w] for w in english_name.split(' ')])

