import networkx as nx
from collections import defaultdict
from family_tree.tree import FamilyTree
from family_tree import entity
import family_tree.utilities as util


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

    def to_tree(self):

        members_graph = read_directory(self.members)
        affiliations_dict = read_affiliations(self.affiliations)

        for badge, affiliations in affiliations_dict.items():

            # TODO remove this try-catch block; it is here to temporarily
            # handle reaffiliates(?), who only have one of their badge numbers
            # actually in the directory
            #
            # TODO apparently this also prevents DZs from entering or something
            try:
                members_graph.node[badge]['record'].affiliations = affiliations
            except KeyError as e:
                pass

        tree = FamilyTree()
        tree.graph = members_graph
        tree.settings = self.settings

        return tree

def read_directory_row(row, graph):

    # TODO move to `tree`????

    member = entity.Member.from_dict(**row)
    if member:
        member_key = member.get_key()
        if member_key in graph and 'record' in graph.node[member_key]:
            # TODO better exception type
            raise Exception('Duplicate badge: "{}"'.format(member_key))
        graph.add_node(member_key, record=member)

read_directory = util.TableReaderFunction(
        read_directory_row,
        nx.DiGraph,
        first_row=2
        )

def read_affiliations_row(row, affiliations_dict):

    badge = row['badge']
    other_badge = '{} {}'.format(
            util.to_greek_name(row['chapter_name']),
            row['other_badge']
            )
    affiliations_dict[badge].append(other_badge)

read_affiliations = util.TableReaderFunction(
        read_affiliations_row,
        lambda : defaultdict(list),
        first_row=2
        )

