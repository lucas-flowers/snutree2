import json, yaml
from voluptuous import Invalid, Required, Schema, All, Exclusive, Any, Coerce, DefaultTo, Extra, Length, Optional, Unique, IsFile
from voluptuous.humanize import validate_with_humanized_errors as validate
from collections import defaultdict
from family_tree.semester import Semester
from family_tree.entity import Knight, Brother, Candidate, Expelled

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

member_status_mapping = {
        'Knight' : Knight,
        'Brother' : Brother,
        'Candidate' : Candidate,
        'Expelled' : Expelled
        }

NonEmptyString = All(str, Length(min=1), msg='must be a nonempty string')

# Matches the schema or None. If it matches None, it uses the constructor of
# schema's class to create a new, presumably empty, object of the right type.
Nullable = lambda schema : Any(schema, DefaultTo(type(schema)()))

# Attribute dicts are arbitrary dicts of Graphviz values.
Attributes = {Extra: Any(str, int, float, bool)}

def MemberType(status_string):

    member_type = member_status_mapping[status_string]

    def validator(string):
        if string == status_string:
            return member_type
        else:
            raise Invalid('status must be one of {{{}}}'.format(', '.join(member_status_mapping.keys())))

    return validator

def SemesterLike(semester_string):

    try:
        return Semester(semester_string)
    except (TypeError, ValueError) as e:
        raise Invalid(str(e))


def Defaults(*categories):
    return { Optional(category) : Attributes for category in categories }

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

    # TODO provide messages for schema

    member_schema = Schema(Any(

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

    # TODO determine what to do when there are missing options
    settings_schema = Schema({
        Required('output') : {
            Required('directory', 'output folder name required') : NonEmptyString,
            Required('name', 'output file name required') : NonEmptyString,
            },
        Exclusive('file', 'sources') : {
            Required('members', 'members CSV required') : NonEmptyString,
            Required('affiliations', 'affiliations CSV required') : NonEmptyString,
            },
        Exclusive('mysql', 'sources') : {
            Required('host', 'SQL hostname required') : NonEmptyString,
            Required('user', 'SQL user required') : NonEmptyString,
            Required('passwd', 'SQL password required') : NonEmptyString,
            Required('port', 'SQL server port required') : int,
            Required('db', 'database name required') : NonEmptyString,
            },
        Optional('extra_members') : IsFile,
        Optional('nodes', default={}) : Nullable({
            Extra : {
                Required('semester') : All(str, Coerce(Semester)), # Semester can coerce int, but we don't want that in settings
                Optional('attributes', default={}) : Nullable(Attributes),
                }
            }),
        Optional('edges', default=[]) : Nullable([{
            Required('nodes') : All([NonEmptyString], Length(min=2)),
            Optional('attributes', default={}) : Nullable(Attributes)
            }]),
        Required('seed') : int,
        Optional('family_colors', default={}) : Nullable({ Extra : NonEmptyString }),
        Required('edge_defaults') : Defaults('all', 'semester', 'unknown'),
        Required('node_defaults') : Defaults('all', 'semester', 'unknown', 'member'),
        Required('graph_defaults') : Defaults('all'),
        }, required=True, extra=False)

    def __init__(self, member_list, affiliations_list, settings_dict):

        self.set_members(member_list)
        self.mark_affiliations(affiliations_list)
        self.set_settings(settings_dict)

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

    def set_settings(self, settings_dict):
        self.settings = validate(settings_dict, self.settings_schema)

    def get_members(self):
        return self._members

def read_settings(path):
    with open(path, 'r') as f:

        # Load into YAML first, then dump into a JSON string, then load again
        # using the json library. This is done because YAML accepts nonstring
        # (i.e., integer) keys, but JSON and Graphviz do not. So if a key in
        # the settings file were an integer, the program's internal
        # representation could end up having two different versions of a node:
        # One with an integer key and another with a string key.
        #
        # This could easily be avoided by just not writing integers in the YAML
        # file, but that could be expecting too much of someone editing it.
        return json.loads(json.dumps(yaml.load(f)))

def to_greek_name(english_name):
    return ''.join([greek_mapping[w] for w in english_name.split(' ')])

