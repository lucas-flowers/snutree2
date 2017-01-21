import networkx as nx
from voluptuous import Schema, Any, All, Length, Optional
from voluptuous.humanize import validate_with_humanized_errors
from collections import defaultdict
from family_tree.tree import FamilyTree
from family_tree.semester import Semester
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
        self._members = []
        self.affiliations = []
        self.settings = {}

    def to_tree(self):

        members_graph = read_directory(self._members)
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

    def set_members(self, members):


        # TODO Reaffiliates cause errors in CSV version
        # Recommend handling reaffiliates in csv.py, since the SQL query will
        # not return any empty reaffiliates
        self._members = [validate_with_humanized_errors(m, self.member_validator)
                for m in members]

    member_validator = Schema({
        'status' : Any('Knight', 'Brother', 'Candidate', 'Expelled'),
        Optional('badge') : str,
        Optional('first_name') : All(str, Length(min=1)),
        Optional('preferred_name') : All(str, Length(min=1)),
        'last_name' : All(str, Length(min=1)),
        Optional('big_badge') : str, # TODO Coerce(int) for /badges/ and str for /keys/
        Optional('pledge_semester') : Semester,
        }, required=True)




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

