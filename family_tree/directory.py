import csv, yaml
import networkx as nx
from networkx.algorithms.operators.binary import compose
from family_tree.tree import FamilyTree
from family_tree import entity
from family_tree import processor

class Directory:
    '''
    TODO merge bnks with directory?

    This class is used to store data from either a CSV file or a SQL query. It
    is an intermediate form before the data is turned into a tree. It stores
    Stores a list of brothers from the directory, a list for brothers not made
    knights, a dictionary of affiliations, and a dictionary of YAML settings.
    '''

    def __init__(self):
        self.members = []
        self.bnks = []
        self.settings = {}

    # TODO move to separate file so that there is no "from_*" methods (maybe?)
    @classmethod
    def from_paths(cls,
            members_path,
            bnks_path=None,
            affiliations_path=None,
            settings_path=None,
            ):

        directory = cls()
        directory.members = read_csv(members_path)
        directory.bnks = read_csv(bnks_path) if bnks_path else []
        directory.settings = read_settings(settings_path) if settings_path else {}

        # affiliations = read_csv(affiliations_path) if affiliations_path else []



        # TODO handle affiliations

        return directory

    def members_to_tree(self):
        return read_directory(self.members)

    def bnks_to_tree(self):
        return read_directory(self.bnks)

    def to_tree(self):

        members_graph = self.members_to_tree()
        bnks_graph = self.bnks_to_tree()

        # TODO add affiliations

        tree = FamilyTree()
        tree.graph = compose(bnks_graph, members_graph) # Second argument attributes overwrite first
        tree.validate_node_existence() # TODO does this belong here?
        tree.settings = self.settings

        return tree

def read_directory_row(row, graph):

    member = entity.Member.from_dict(**row)
    if member:
        member_key = member.get_key()
        if member_key in graph and 'record' in graph.node[member_key]:
            # TODO better exception type
            raise Exception('Duplicate badge: "{}"'.format(member_key))
        graph.add_node(member_key, record=member)
        if member.parent:
            graph.add_edge(member.parent, member_key)

read_directory = processor.iterate(read_directory_row, nx.DiGraph, start_index=2)


#
# greek_mapping = {
#         'Alpha' : 'A',
#         'Beta' : 'B',
#         'Gamma' : 'Γ',
#         'Delta' : 'Δ',
#         'Epsilon' : 'E',
#         'Zeta' : 'Z',
#         'Eta' : 'H',
#         'Theta' : 'Θ',
#         'Iota' : 'I',
#         'Kappa' : 'K',
#         'Lambda' : 'Λ',
#         'Mu' : 'M',
#         'Nu' : 'N',
#         'Xi' : 'Ξ',
#         'Omicron' : 'O',
#         'Pi' : 'Π',
#         'Rho' : 'P',
#         'Sigma' : 'Σ',
#         'Tau' : 'T',
#         'Upsilon' : 'Y',
#         'Phi' : 'Φ',
#         'Chi' : 'X',
#         'Psi' : 'Ψ',
#         'Omega' : 'Ω',
#         '(A)' : '(A)',
#         '(B)' : '(B)',
#         }
#
# # intermediate += affiliations
# def process_affiliation(row, affiliations):
#     badge = row['badge']
#     other_badge = '{}  {}'.format(
#             to_greek_name(row['chapter_name']),
#             row['other_badge'])
#     affiliations[badge].append(other_badge)
# def to_greek_name(english_name):
#     return ''.join([greek_mapping[w] for w in english_name.split(' ')])
# process_affiliations = processor.iterate(
#         process_affiliation,
#         lambda : defaultdict(list),
#         2)
# affiliations = process_affiliations(affiliations)
#
def read_csv(path):
    with open(path, 'r') as f:
        return list(csv.DictReader(f))

def read_settings(path):
    with open(path, 'r') as f:
        return yaml.load(f.read())





