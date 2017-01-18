import random
from networkx.algorithms import dag
from networkx.algorithms.operators.binary import compose
from networkx.algorithms.components import weakly_connected_components
import family_tree.file as rdr
from family_tree import dot
from family_tree.semester import semester_range
from family_tree.color import graphviz_color_map

# TODO remove when Member call is removed
from family_tree import entity

class FamilyTree:

    def __init__(self, graph=None, settings=None):
        self.graph = graph
        self.settings = {} or settings # TODO handle empty settings

    ###########################################################################
    #### Generation                                                        ####
    ###########################################################################

    # TODO handle when variable paths are empty
    @classmethod
    def from_paths(cls,
        directory_path=None,
        bnks_path=None,
        affiliations_path=None,
        settings_path=None,
        ):

        tree = cls()

        affiliations = rdr.AffiliationsReader.from_path(affiliations_path).read()

        main_graph = rdr.DirectoryReader.from_path(directory_path, affiliations).read()
        bnks_graph = rdr.DirectoryReader.from_path(bnks_path).read()

        # Second argument attributes overwrite first
        tree.graph = compose(bnks_graph, main_graph)

        tree.validate_node_existence()

        tree.settings = rdr.SettingsReader.from_path(settings_path).read()

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

            + All valid entries corresponding to the key in the `badge` column
            are guaranteed to be added as records

            + Invalid values for `big_badge` that cannot be interpreted as
            integers are already caught when reading chapter nodes (TODO figure
            out what this means because chapter nodes have been removed from
            this program)
        '''

        for key, node_dict in self.graph.nodes_iter(data=True):
            if 'record' not in node_dict:
                child = next(self.graph.successors_iter(key))
                raise rdr.DirectoryError('Brother with badge {} has unknown big brother: "{}"'.format(child, key))

    ###########################################################################
    #### Decoration                                                        ####
    ###########################################################################

    def decorate(self):

        self.remove_singletons()
        self.add_families()
        self.add_orphan_parents()
        self.add_node_attributes()
        self.add_colors()
        self.add_edge_attributes()

    def remove_singletons(self):

        self.graph.remove_nodes_from([key for key, degree in self.graph.degree_iter() if degree == 0])

    def add_node_attributes(self):

        for key, node_dict in self.graph.nodes_iter(data=True):
            record = node_dict['record']
            attributes = node_dict.get('dot_node_attributes', {})
            attributes.update(record.dot_node_attributes())
            node_dict['dot_node_attributes'] = attributes

    def add_edge_attributes(self):

        for parent_key, child_key, edge_dict in self.graph.edges_iter(data=True):
            parent_record = self.graph.node[parent_key]['record']
            child_record = self.graph.node[child_key]['record']
            attributes = edge_dict.get('dot_edge_attributes', {})
            attributes.update(parent_record.dot_edge_attributes(child_record))
            edge_dict['dot_edge_attributes'] = attributes

    def add_families(self):

        # Members-only graph
        members_only = self.graph.subgraph(
                [key for key, node_dict in self.graph.nodes_iter(data=True)
                    if isinstance(node_dict['record'], entity.Member)]
                )

        # Find heads of members-only graph
        family_heads = [key for key, in_degree in members_only.in_degree().items()
                if in_degree == 0]

        # Mark descendants of the heads
        for head_key in family_heads:
            self.graph.node[head_key]['family'] = head_key
            for descendant_key in dag.descendants(members_only, head_key):
                self.graph.node[descendant_key]['family'] = head_key

    def add_orphan_parents(self):

        # Find members that had big brothers whose identities are unknown
        orphan_keys = [
                key for key, in_degree in self.graph.in_degree().items()
                if in_degree == 0 and isinstance(self.graph.node[key]['record'], entity.Member)
                ]

        for orphan_key in orphan_keys:
            parent_record = entity.UnidentifiedKnight.from_member(self.graph.node[orphan_key]['record'])
            parent_key = parent_record.get_key()
            self.graph.add_node(parent_key, record=parent_record, dot_node_attributes=self.settings['graphviz']['node_defaults']['unknown'])
            self.graph.add_edge(parent_key, orphan_key, dot_edge_attributes=self.settings['graphviz']['edge_defaults']['unknown'])

    ###########################################################################
    #### Convert to DOT                                                    ####
    ###########################################################################

    def add_colors(self):

        family_color_map = graphviz_color_map(initial_mappings=self.settings['graphviz']['family_colors'])
        for key, node_dict in self.graph.nodes_iter(data=True):
            if isinstance(node_dict['record'], entity.Member):
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
                attributes=self.settings['graphviz']['graph_defaults']['all'],
                node_defaults=self.settings['graphviz']['node_defaults']['all'],
                edge_defaults=self.settings['graphviz']['edge_defaults']['all'],
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
                node_defaults=self.settings['graphviz']['node_defaults']['semester'],
                edge_defaults=self.settings['graphviz']['edge_defaults']['semester'],
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

        dotgraph = dot.Graph(
                key,
                'subgraph',
                node_defaults=self.settings['graphviz']['node_defaults']['member']
                )

        nodes = []
        for key, node_dict in self.ordered_nodes():
            nodes.append(dot.Node(key, node_dict['dot_node_attributes']))

        edges = []
        for parent_key, child_key, edge_dict in self.ordered_edges():
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

    ###########################################################################
    #### Ordering                                                          ####
    ###########################################################################

    def ordered_nodes(self):
        '''
        An iterator over this graph's nodes and node dictionaries, in the order
        they should be printed.
        '''

        # Find the different connected components of the graph (i.e., each
        # component is a different family, unless it includes a reorganization
        # node which can connect unrelated families). (TODO remove reference to
        # reorganization in this comment.)
        #
        # Add the nodes from each component to the DOT graph, in the order of
        # component. The order of components is randomized to help prevent
        # strange behavior (e.g., excessively long nodes) and allow the user to
        # change the graph by choosing a different random seed if the graph is
        # not aesthetic. (The previous method placed nodes in the source code
        # by the order found, but that consistently produced ugly results.)
        #
        # There might be a specific order that would be satisfactory, but
        # randomizing is easier for now. A user could of course manually adjust
        # nodes, but I want to avoid having the potentially unskilled user
        # change DOT source code or fiddle with DOT attributes.
        #
        # (The components themselves and their members' edges (see
        # self.ordered_edges() are not randomized)
        components = sorted(list(weakly_connected_components(self.graph)), key=lambda x : min(map(str, x)))
        rng = random.Random(self.settings['graphviz']['seed'])
        rng.shuffle(components)
        for component in components:
            for key in sorted(component, key=str):
                yield key, self.graph.node[key]

    def ordered_edges(self):
        '''
        An iterator over this graph's edges and edge dictionaries, in the order
        they should be printed.
        '''

        # Sort the list of edges by parent then child key (the `t` in lambda is
        # a 3-tuple of the form (parent, child, edge_dict)). Ensures the order
        # of edges printed to source is the identical for the same input data.
        edges = sorted(self.graph.edges(data=True), key=lambda t : tuple(map(str, t[:-1])))

        yield from edges

