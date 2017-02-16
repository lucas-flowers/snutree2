from pprint import pformat
from collections import defaultdict
from cerberus import Validator
from .utilities import logged, nonempty_string

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

class Directory:
    '''
    This class is used to store data from either a CSV file or a SQL query. It
    is an intermediate form before the data is turned into a tree. It stores a
    list of brothers from the directory (with affiliations) and a dictionary of
    YAML settings.

    The Directory class guarantees that entries in its members and affiliations
    lists will be dictionaries that follow the following schema. Furthermore,
    the class guarantees that all chapter_name/other_badge pairs in the
    affiliations are unique.
    '''

    affiliations_schema = Validator({
        'badge' : nonempty_string,
        'chapter_name' : { 'required' : True, 'coerce' : to_greek_name },
        'other_badge' : nonempty_string
        })

    def __init__(self, member_list, affiliations_list, settings_dict, member_types):

        self.member_schemas = {}
        for typ in member_types:
            for allowed in typ.schema['status']['allowed']:
                self.member_schemas[allowed] = typ.get_schema()

        self.settings = settings_dict
        self.set_members(member_list)
        self.mark_affiliations(affiliations_list)

    @logged
    def set_members(self, members):

        member_status_map = defaultdict(list)
        for member in members:

            # Make sure the member status field is valid first
            if member.get('status') not in self.member_schemas.keys():
                msg = 'Invalid member status in:\n{}\nStatus must be one of:\n{}'
                vals = pformat(member), list(self.member_schemas.keys())
                raise DirectoryError(msg.format(*vals))

            member_status_map[member['status']].append(member)

        members_list = []
        for status, members in member_status_map.items():

            validator = Validator({'members' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'dict',
                    'schema' : self.member_schemas[status]['schema']
                    }
                }})

            if not validator.validate({'members' : members}):
                errors = []
                for member_errors in validator.errors['members']:
                    for i, error in member_errors.items():
                        errors.append({
                            'Invalid {}'.format(status) : validator.document['members'][i],
                            'Rules Violated' : error
                            })
                msg = 'Errors found in directory:\n{}'
                raise DirectoryError(msg.format(pformat(errors)))

            members_list += validator.document['members']

        # Create member object from the normalized dict and add to list
        self._members = []
        for member in members_list:
            MemberType = self.member_schemas[member['status']]['constructor']
            self._members.append(MemberType(**member))

    @logged
    def mark_affiliations(self, affiliations):

        affiliations_map = defaultdict(list)
        used_affiliations = set()
        for affiliation in affiliations:

            # Validate affiliation format
            if not self.affiliations_schema.validate(affiliation):
                msg = 'Invalid affiliation:\n{}\nRules violated:\n{}'
                vals = pformat(affiliation), pformat(self.affiliations_schema.errors)
                raise DirectoryError(msg.format(*vals))

            # Catch duplicate affiliations
            chapter_name = affiliation['chapter_name']
            other_badge = affiliation['other_badge']
            if (chapter_name, other_badge) in used_affiliations:
                msg = 'Duplicate affiliation:\n{}\nBased on key:\n{}'
                vals = pformat(affiliation), (chapter_name, other_badge)
                raise DirectoryError(msg.format(*vals))
            else:
                used_affiliations.add((chapter_name, other_badge))

            # Used normalized dict
            affiliation = self.affiliations_schema.document
            badge = affiliation['badge']
            chapter_designation = affiliation['chapter_name'] # Normalized
            other_badge = affiliation['other_badge']

            # Add affiliation to the mapping
            other_designation = '{} {}'.format(chapter_designation, other_badge)
            affiliations_map[badge].append(other_designation)

        # Add all affiliations to the respective members
        for member in self._members:
            member.affiliations = affiliations_map[member.get_key()]

    def get_members(self):
        return self._members

class DirectoryError(Exception):
    pass

