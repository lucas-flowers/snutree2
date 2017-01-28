import yaml
from voluptuous import Schema, Unique
from voluptuous.humanize import validate_with_humanized_errors as validate
from collections import defaultdict
from family_tree import schema

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

    def __init__(self, member_list, affiliations_list, settings_dict):

        self.set_members(member_list)
        self.mark_affiliations(affiliations_list)
        self.set_settings(settings_dict)

    def set_members(self, members):

        members = [validate(m, schema.member_schema) for m in members]
        validate([m['badge'] for m in members if 'badge' in m], Schema(Unique()))

        self._members = []
        for row in members:
            MemberType = row['status']
            self._members.append(MemberType(**row))

    def mark_affiliations(self, affiliations):

        affiliations = [validate(a, schema.affiliations_schema) for a in affiliations]
        validate([(a['chapter_name'], a['other_badge']) for a in affiliations], Schema(Unique()))

        affiliations_map = defaultdict(list)
        for row in affiliations:
            badge = row['badge']
            other_badge = '{} {}'.format(to_greek_name(row['chapter_name']), row['other_badge'])
            affiliations_map[badge].append(other_badge)

        for member in self._members:
            member.affiliations = affiliations_map[member.get_key()]

    def set_settings(self, settings_dict):
        # TODO figure out where to put all settings schema and functions; this
        # used to have a validation function
        self.settings = settings_dict

    def get_members(self):
        return self._members

def retrieve_settings(path):

    with open(path, 'r') as f:
        settings = yaml.load(f)

    settings = schema.settings_schema.validated(settings)
    if settings:
        return settings
    else:
        raise Exception(str(schema.settings_schema.errors))


def to_greek_name(english_name):
    return ''.join([greek_mapping[w] for w in english_name.split(' ')])

