import json, yaml
from voluptuous import Schema, All, PathExists, Exclusive, Any, Coerce, DefaultTo, Extra, Length, Optional, Unique, IsFile
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

NonEmptyString = All(str, Length(min=1))

# Matches the schema or None. If it matches None, it uses the constructor of
# schema's class to create a new, presumably empty, object of the right type.
Nullable = lambda schema : Any(schema, DefaultTo(type(schema)()))

# Attribute dicts are arbitrary dicts of Graphviz values.
Attributes = {Extra: Any(str, int, float, bool)}

def MemberType(status):
    member_type = member_status_mapping.get(status, None)
    if member_type:
        return member_type
    else:
        raise ValueError('Status must be one of {}'.format(member_status_mapping.keys()))

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
            'status' : MemberType,
            'badge' : NonEmptyString,
            'first_name' : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            'last_name' : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : Semester,
            },

        {
            'status' : MemberType,
            Optional('first_name') : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            'last_name' : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : Semester,
            },

        {
            'status' : MemberType,
            'first_name' : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            'last_name' : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : Semester,
            },

        {
            'status' : MemberType,
            'badge' : NonEmptyString,
            Optional('first_name') : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            Optional('last_name') : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : Semester,
            },

        ), required=True, extra=False)

    affiliations_schema = Schema({
        'badge' : NonEmptyString,
        'chapter_name' : NonEmptyString,
        'other_badge' : NonEmptyString,
        })

    # TODO determine what to do when there are missing options
    settings_schema = Schema({
        'output' : {
            'directory' : PathExists,
            'name' : NonEmptyString,
            },
        Exclusive('file', 'sources') : {
            'members' : IsFile,
            'affiliations' : IsFile,
            },
        Exclusive('mysql', 'sources') : {
            'host' : NonEmptyString,
            'user' : NonEmptyString,
            'passwd' : NonEmptyString,
            'port' : int,
            'db' : NonEmptyString,
            },
        Optional('extra_members') : IsFile,
        Optional('nodes', default={}) : Nullable({
            Extra : {
                'semester' : All(str, Coerce(Semester)), # Semester can coerce int, but we don't want that in settings
                Optional('attributes', default={}) : Nullable(Attributes),
                }
            }),
        Optional('edges', default=[]) : Nullable([{
            'nodes' : All([NonEmptyString], Length(min=2)),
            Optional('attributes', default={}) : Nullable(Attributes)
            }]),
        'seed' : int,
        Optional('family_colors', default={}) : Nullable({ Extra : NonEmptyString }),
        'edge_defaults' : Defaults('all', 'semester', 'unknown'),
        'node_defaults' : Defaults('all', 'semester', 'unknown', 'member'),
        'graph_defaults' : Defaults('all'),
        }, required=True, extra=False)

    def __init__(self, member_list, affiliations_list, settings_dict):

        self.set_members(member_list)
        self.mark_affiliations(affiliations_list)
        self.set_settings(settings_dict)

    def set_members(self, members):

        validate([m['badge'] for m in members if 'badge' in m], Schema(Unique()))
        members = [validate(m, self.member_schema) for m in members]

        self._members = []
        for row in members:
            MemberType = row['status']
            self._members.append(MemberType(**row))

    def mark_affiliations(self, affiliations):

        validate([(a['chapter_name'], a['other_badge']) for a in affiliations], Schema(Unique()))
        affiliations = [validate(a, self.affiliations_schema) for a in affiliations]

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

