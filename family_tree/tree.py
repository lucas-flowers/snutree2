import networkx as nx
from networkx.algorithms import dag
from networkx.algorithms.operators.binary import compose
from family_tree.file import *
from family_tree import dot
from family_tree.semester import semester_range
from family_tree.color import graphviz_color_map

# TODO remove when MemberRecord call is removed
from family_tree.records import MemberRecord

graph_defaults = {
        'size' : 80,
        'ratio' : 'compress',
        'pad' : '.5, .5',
        'ranksep' : .3,
        }

node_defaults = {
        'style' : 'filled',
        'shape' : 'box',
        'penwidth' : 2,
        'width' : 2,
        'height' : .45,
        'fontname' : 'dejavu sans',
        }

edge_defaults = {
        'arrowhead' : 'none',
        }

member_node_defaults = {
        'fillcolor' : '0.11 .71 1.0',
        }

semester_edge_defaults = {
        'style' : 'invis',
        }

semester_node_defaults = {
        'color' : 'none',
        'fontsize' : 20,
        'fontname' : 'georgia',
        }

class FamilyTree:

    def __init__(self, graph=None, family_colors=None):
        self.graph = graph
        self.family_colors = {} or family_colors

    ###########################################################################
    #### Generation                                                        ####
    ###########################################################################

    # TODO handle when variables paths are empty
    @classmethod
    def from_paths(cls,
        directory_path=None,
        chapter_path=None,
        bnks_path=None,
        color_path=None
        ):

        tree = cls()

        chapter_locations = ChapterReader.from_path(chapter_path).read()

        main_graph = DirectoryReader.from_path(directory_path, chapter_locations).read()
        bnks_graph = DirectoryReader.from_path(bnks_path, chapter_locations).read()

        # Second argument attributes overwrite first
        tree.graph = compose(bnks_graph, main_graph)

        tree.family_colors = FamilyColorReader.from_path(color_path).read()

        tree.validate_node_existence()

        return tree

    def validate_node_existence(self):
        '''
        Action
        ======

        Checks for uninitialized nodes in the graph: If a node key not have a
        record associated with it, then the key only ever appeared as part of
        an edge when reading the graph into memory.

        This is only possible when the `big_badge` field in the directory is a
        badge number with no corresponding member record, because:

            + Reorganization and Chapter nodes are added *only* when they exist

            + All valid entries corresponding to the key in the `badge` column
            are guaranteed to be added as records

            + Invalid values for `big_badge` that cannot be interpreted as
            integers are already caught when reading chapter nodes
        '''

        for key, node_dict in self.graph.nodes_iter(data=True):
            if 'record' not in node_dict:
                child = next(self.graph.successors_iter(key))
                raise DirectoryError('Brother with badge {} has unknown big brother: "{}"'.format(child, key))

    ###########################################################################
    #### Decoration                                                        ####
    ###########################################################################

    def decorate(self):

        self.kill_orphans()
        self.add_families()
        self.add_node_attributes()
        self.add_colors()
        self.add_edge_attributes()

    def kill_orphans(self):

        self.graph.remove_nodes_from([key for key, degree in self.graph.degree_iter() if degree == 0])

    def add_node_attributes(self):

        for key, node_dict in self.graph.nodes_iter(data=True):
            record = node_dict['record']
            node_dict['dot_node_attributes'] = record.dot_node_attributes()

    def add_edge_attributes(self):

        for parent_key, child_key, edge_dict in self.graph.edges_iter(data=True):
            parent_record = self.graph.node[parent_key]['record']
            child_record = self.graph.node[child_key]['record']
            edge_dict['dot_edge_attributes'] = \
                    parent_record.dot_edge_attributes(child_record)

    def add_families(self):

        # Members-only graph
        members_only = self.graph.subgraph(
                [key for key, node_dict in self.graph.nodes_iter(data=True)
                    if isinstance(node_dict['record'], MemberRecord)]
                )

        # Find heads of members-only graph
        family_heads = [key for key, in_degree in members_only.in_degree().items()
                if in_degree == 0]

        # Mark descendants of the heads
        for head_key in family_heads:
            self.graph.node[head_key]['family'] = head_key
            for descendant_key in dag.descendants(members_only, head_key):
                self.graph.node[descendant_key]['family'] = head_key

    ###########################################################################
    #### Convert to DOT                                                    ####
    ###########################################################################

    def add_colors(self):

        family_color_map = graphviz_color_map(initial_mappings=self.family_colors)
        for key, node_dict in self.graph.nodes_iter(data=True):
            if isinstance(node_dict['record'], MemberRecord):
                node_dict['dot_node_attributes']['color'] = family_color_map[node_dict['family']]


    def to_dot_graph(self):

        min_semester, max_semester = self.get_semester_bounds()
        dates_left = self.create_date_subgraph('L', min_semester, max_semester)
        dates_right = self.create_date_subgraph('R', min_semester, max_semester)
        tree = self.create_tree_subgraph('members')
        ranks = self.create_ranks()

        dotgraph = dot.Graph(
                'family_tree',
                'digraph',
                attributes=graph_defaults,
                node_defaults=node_defaults,
                edge_defaults=edge_defaults,
                )
        dotgraph.children = [dates_left, tree, dates_right] + ranks

        return dotgraph

    def get_semester_bounds(self):
        min_sem = float('inf')
        max_sem = float('-inf')
        for _, node_dict in self.graph.nodes_iter(data=True):
            semester = node_dict['record'].semester
            if semester and min_sem > semester:
                min_sem = semester
            if semester and max_sem < semester:
                max_sem = semester
        return min_sem, max_sem

    def create_date_subgraph(self, key, min_semester, max_semester):

        subgraph = dot.Graph(
                'dates{}'.format(key),
                'subgraph',
                node_defaults=semester_node_defaults,
                edge_defaults=semester_edge_defaults,
                )

        nodes = []
        edges = []
        for sem in semester_range(min_semester, max_semester+1):
            nodes.append(dot.Node(
                '{}{}'.format(sem, key),
                {'label' : sem},
                ))
            edges.append(dot.Edge(
                '{}{}'.format(sem, key),
                '{}{}'.format(sem+1, key),
                ))

        sem += 1
        nodes.append(dot.Node(
            '{}{}'.format(sem, key),
            {'label' : sem},
            ))

        subgraph.children = nodes + edges

        return subgraph

    def create_tree_subgraph(self, key):

        dotgraph = dot.Graph(key, 'subgraph', node_defaults=member_node_defaults)

        nodes = []
        for key, node_dict in self.graph.nodes_iter(data=True):
            nodes.append(dot.Node(key, node_dict['dot_node_attributes']))

        edges = []
        for parent_key, child_key, edge_dict in self.graph.edges(data=True):
            edges.append(dot.Edge(parent_key, child_key, edge_dict['dot_edge_attributes']))

        dotgraph.children = nodes + edges

        return dotgraph

    def create_ranks(self):

        ranks = {}
        for key, node_dict in self.graph.nodes(data=True):
            semester = node_dict['record'].semester
            if semester in ranks:
                ranks[semester].keys.append(key)
            else:
                ranks[semester] = dot.Rank([
                        '{}L'.format(semester),
                        '{}R'.format(semester),
                        key,
                        ])

        return list(ranks.values())

