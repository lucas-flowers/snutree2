import csv, yaml
import networkx as nx
from collections import defaultdict
from family_tree.tree import FamilyTree
from family_tree import entity

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
        '(A)' : '(A)',
        '(B)' : '(B)',
        }

class Directory:
    '''
    This class is used to store data from either a CSV file or a SQL query. It
    is an intermediate form before the data is turned into a tree. It stores
    Stores a list of brothers from the directory, a list for brothers not made
    knights, a dictionary of affiliations, and a dictionary of YAML settings.
    '''

    def __init__(self):
        self.members = []
        self.affiliations = []
        self.settings = {}

    # TODO move to separate file so that there is no "from_*" methods (maybe?)
    @classmethod
    def from_paths(cls,
            members_path,
            extra_members_path=None, # Intended for brothers not made knights
            affiliations_path=None,
            settings_path=None,
            ):

        directory = cls()
        directory.members = read_csv(members_path) + (read_csv(extra_members_path) if extra_members_path else [])
        directory.affiliations = read_csv(affiliations_path) if affiliations_path else []
        directory.settings = read_settings(settings_path) if settings_path else {}

        return directory

    def to_tree(self):

        members_graph = read_directory(self.members)
        affiliations_dict = read_affiliations(self.affiliations)

        for badge, affiliations in affiliations_dict.items():
            members_graph.node[badge]['record'].affiliations = affiliations

        tree = FamilyTree()
        tree.graph = members_graph
        tree.settings = self.settings

        return tree

def table_reader(read_row, container_type, first_row=1):
    '''
    Returns a function `read_all` that uses `read_row` to read each "row" in an
    iterable (`table` below). The function `read_row` should store each row in
    `container`, which is of type `container_type`.

    The `read_all` function keeps track of the row number and provides the row
    number when an exception is raised. The starting row number defaults to 1,
    but can be changed (i.e., for CSVs with headers).
    '''

    def read_all(table):

        container = container_type()
        row_number = first_row
        try:
            for row in table:
                read_row(row, container)
                row_number += 1
        except:
            # TODO use a real error, replace "row" with something more
            # appropriate
            raise Exception('Error in row {}'.format(row_number))

        return container

    return read_all


def read_directory_row(row, graph):

    # TODO move to `tree`????

    member = entity.Member.from_dict(**row)
    if member:
        member_key = member.get_key()
        if member_key in graph and 'record' in graph.node[member_key]:
            # TODO better exception type
            raise Exception('Duplicate badge: "{}"'.format(member_key))
        graph.add_node(member_key, record=member)

read_directory = table_reader(
        read_directory_row,
        nx.DiGraph,
        first_row=2
        )

def read_affiliations_row(row, affiliations_dict):

    badge = int(row['badge'])
    other_badge = '{} {}'.format(
            to_greek_name(row['chapter_name']),
            row['other_badge']
            )
    affiliations_dict[badge].append(other_badge)

read_affiliations = table_reader(
        read_affiliations_row,
        lambda : defaultdict(list),
        first_row=2
        )

def read_csv(path):
    with open(path, 'r') as f:
        return list(csv.DictReader(f))

def read_settings(path):
    with open(path, 'r') as f:
        return yaml.load(f.read())

def to_greek_name(english_name):
    return ''.join([greek_mapping[w] for w in english_name.split(' ')])



