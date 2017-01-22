import networkx as nx
from voluptuous import Schema, All, Any, Length, Optional, Unique
from voluptuous.humanize import validate_with_humanized_errors as validate
from collections import defaultdict
from family_tree.tree import FamilyTree
from family_tree.semester import Semester
from family_tree import entity
import family_tree.utilities as util

NonEmptyString = All(str, Length(min=1))

class Directory:
    '''
    This class is used to store data from either a CSV file or a SQL query. It
    is an intermediate form before the data is turned into a tree. It stores a
    list of brothers from the directory, a list for brothers not made knights,
    a dictionary of affiliations, and a dictionary of YAML settings.
    '''

    # The Directory class guarantees that entries in its members and
    # affiliations lists will be dictionaries that follow the following schema.
    #
    # Furthermore, the class guarantees that all members in the member list are
    # unique (as determined by their badge), and that all
    # chapter_name/other_badge pairs in the affiliations list are unique.

    member_schema = Schema(Any(

        {
            'status' : 'Knight',
            'badge' : NonEmptyString,
            'first_name' : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            'last_name' : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : Semester,
            },

        {
            'status' : 'Brother',
            Optional('first_name') : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            'last_name' : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : Semester,
            },

        {
            'status' : 'Candidate',
            'first_name' : NonEmptyString,
            Optional('preferred_name') : NonEmptyString,
            'last_name' : NonEmptyString,
            Optional('big_badge') : NonEmptyString,
            Optional('pledge_semester') : Semester,
            },

        {
            'status' : 'Expelled',
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

    def __init__(self):
        self._members = []
        self._affiliations = []
        self.settings = {}

    def to_tree(self):

        members_graph = read_directory(self._members)
        affiliations_dict = read_affiliations(self._affiliations)

        for badge, affiliations in affiliations_dict.items():

            members_graph.node[badge]['record'].affiliations = affiliations

        tree = FamilyTree()
        tree.graph = members_graph
        tree.settings = self.settings

        return tree

    def set_members(self, members):
        validate([m['badge'] for m in members if 'badge' in m], Schema(Unique()))
        self._members = [validate(m, self.member_schema) for m in members]

    def set_affiliations(self, affiliations):
        validate([(a['chapter_name'], a['other_badge']) for a in affiliations], Schema(Unique()))
        self._affiliations = [validate(a, self.affiliations_schema) for a in affiliations]

def read_directory_row(row, graph):

    # TODO move to `tree`????

    member = entity.Member.from_dict(row)
    if member:
        graph.add_node(member.get_key(), record=member)

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

