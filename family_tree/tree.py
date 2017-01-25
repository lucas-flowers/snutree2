import random
import networkx as nx
from networkx.algorithms.components import weakly_connected_components
from family_tree import dot
from family_tree.color import graphviz_colors
from family_tree.semester import semester_range

# TODO remove when Member call is removed (calls to Member should be removed if
# possible)
from family_tree import entity

class FamilyTree:

    def __init__(self, directory):

        self.graph = nx.DiGraph()
        self.settings = directory.settings

        self.add_members(directory.get_members())

        # TODO add the following as options to settings. use special decorators
        # to mark the options?

        self.add_relationships()
        self.add_custom_nodes()
        self.add_custom_edges()
        self.remove_singleton_members() # ^ add_member, add_edges, add_custom_edges
        self.mark_families()
        self.add_orphan_parents()
        self.add_colors()

    ###########################################################################
    #### Utilities                                                         ####
    ###########################################################################

    def nodes_iter(self, *attributes, node_dict=False):
        '''
        Iterates over the nodes in the graph by yielding a tuple with the key
        first, followed by the fields asked for in the *fields arguments in
        the same order asked.

        If node_dict=True, then a the entire attribute dictionary is also
        provided at the end of the tuple.
        '''
        for key in list(self.graph.nodes_iter()):
            yield (key,
                    *(self.graph.node[key][attr] for attr in attributes)) + \
                    ((self.graph.node[key],) if node_dict else ())

    def add_entity(self, entity):
        self.graph.add_node(entity.get_key(), entity=entity,
                dot_attributes=entity.dot_attributes())

    def add_relationship(self, parent_key, child_key, dot_attributes=None):
        self.graph.add_edge(parent_key, child_key,
                dot_attributes = dot_attributes or {})

    ###########################################################################
    #### Decoration                                                        ####
    ###########################################################################

    def add_members(self, member_list):
        '''
        Add the members to the graph.
        '''

        for member in member_list:
            self.add_entity(member)

    def add_custom_nodes(self):
        '''
        Add all custom nodes loaded from settings.
        '''

        for key, value in self.settings['nodes'].items():
            self.add_entity(entity.Custom(key, **value))

    def add_custom_edges(self):
        '''
        Add all custom edges loaded from settings.
        '''

        for path in self.settings['edges']:
            nodes = path['nodes']
            attributes = path['attributes']
            edges = [(u, v) for u, v in zip(nodes[:-1], nodes[1:])]
            self.graph.add_edges_from(edges, dot_attributes=attributes)

    def add_relationships(self):
        '''
        Connect all entities in the tree by finding each entity's parent and
        adding the edge (parent, entity).
        '''

        for key, member in self.nodes_iter('entity'):
            if member.parent:
                if member.parent in self.graph:
                    self.add_relationship(member.parent, key)
                else:
                    raise TreeException('Node with key "{}" has unknown parent node: "{}"'.format(key, member.parent))

    def remove_singleton_members(self):
        '''
        Remove all members in the tree whose nodes neither have parents nor
        children, as determined by the node's degree (including both in-edges
        and out-edges).
        '''

        # TODO protect singletons (e.g., refounders without littles) after a
        # certain date so they don't disappear without at least a warning?
        singletons = [key for key, degree in self.graph.degree_iter() if degree == 0
                and isinstance(self.graph.node[key]['entity'], entity.Member)]

        self.graph.remove_nodes_from(singletons)

    def mark_families(self):

        # Members-only graph
        members_only = self.graph.subgraph(
                [key for key, member in self.nodes_iter('entity')
                    if isinstance(member, entity.Member)]
                )

        # Families are weakly connected components of the members-only graph
        families = weakly_connected_components(members_only)

        # Add a pointer to each member's family subgraph
        for family in families:
            family_dict = {}
            for key in family:
                self.graph.node[key]['family'] = family_dict

    def add_orphan_parents(self):
        '''
        Add custom entities as parents to members whose nodes have no parents,
        as determined by the nodes' in-degrees.

        Note: This must occur after edges are generated in order to determine
        degrees. But it must also occur after singletons are removed, because
        many singletons do not have well-formed pledge class semester values in
        the directory (and determining pledge class semester values accurately
        is not simple enough for me to bother doing). If ever pledge class
        semesters were filled in, this could occur before add_edges and we can
        remove some of the extra code in this function that would normally be
        done by add_XXX_attributes.
        '''

        orphan_keys = [key
                for key, in_degree
                in self.graph.in_degree().items()
                if in_degree == 0
                and isinstance(self.graph.node[key]['entity'], entity.Member)
                ]

        for orphan_key in orphan_keys:

            orphan = self.graph.node[orphan_key]['entity']

            parent = entity.UnidentifiedKnight(orphan,
                    self.settings['node_defaults']['unknown'])
            parent_key = parent.get_key()

            # Set orphan parent
            orphan.parent = parent.get_key()

            self.add_entity(parent)
            self.add_relationship(parent_key, orphan_key,
                    dot_attributes=self.settings['edge_defaults']['unknown'])

    ###########################################################################
    #### Convert to DOT                                                    ####
    ###########################################################################

    def add_colors(self):
        '''
        Add colors to member nodes, based on their family. Uses settings
        dictionary to provide initial colors, and generates the rest as needed.
        '''

        family_colors = self.settings['family_colors']
        other_colors = graphviz_colors()

        for key, color in family_colors.items():
            # TODO error check if the key is actually a member
            other_colors.discard(color)
            # TODO handle what happens when a family has more than one color
            self.graph.node[key]['family']['color'] = color

        # The nodes are sorted first, to ensure that the same colors are used
        # for the same input data.
        for key, node_dict in sorted(self.graph.nodes_iter(data=True)):
            if isinstance(node_dict['entity'], entity.Member):
                family_dict = node_dict['family']
                if 'color' not in family_dict:
                    color = other_colors.pop()
                    family_dict['color'] = color
                node_dict['dot_attributes']['color'] = family_dict['color']

    def to_dot_graph(self):

        min_semester, max_semester = self.get_semester_bounds()
        dates_left = self.create_date_subgraph('L', min_semester, max_semester)
        dates_right = self.create_date_subgraph('R', min_semester, max_semester)
        tree = self.create_tree_subgraph('members')
        ranks = self.create_ranks()

        dotgraph = dot.Graph(
                'family_tree',
                'digraph',
                attributes=self.settings['graph_defaults']['all'],
                node_defaults=self.settings['node_defaults']['all'],
                edge_defaults=self.settings['edge_defaults']['all'],
                )
        dotgraph.children = [dates_left, tree, dates_right] + ranks

        return dotgraph

    def get_semester_bounds(self):
        min_sem = float('inf')
        max_sem = float('-inf')
        for _, node_dict in self.graph.nodes_iter(data=True):
            semester = node_dict['entity'].semester
            if semester and min_sem > semester:
                min_sem = semester
            if semester and max_sem < semester:
                max_sem = semester
        return min_sem, max_sem

    def create_date_subgraph(self, key, min_semester, max_semester):

        subgraph = dot.Graph(
                'dates{}'.format(key),
                'subgraph',
                node_defaults=self.settings['node_defaults']['semester'],
                edge_defaults=self.settings['edge_defaults']['semester'],
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
                node_defaults=self.settings['node_defaults']['member']
                )

        nodes = []
        for key, node_dict in self.ordered_nodes():
            nodes.append(dot.Node(key, node_dict['dot_attributes']))

        edges = []
        for parent_key, child_key, edge_dict in self.ordered_edges():
            edges.append(dot.Edge(parent_key, child_key, edge_dict['dot_attributes']))

        dotgraph.children = nodes + edges

        return dotgraph

    def create_ranks(self):

        ranks = {}
        for key, node_dict in self.graph.nodes(data=True):
            semester = node_dict['entity'].semester
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

        First: The (weakly) connected components of the graph are put in a
        list. The components are then sorted by the minimum
        (lexicographically-speaking) key they contain. Then, the random seed in
        the settings dictionary is used to shuffle the components. A few notes:

            + The components are randomized because strange behavior might
            occur if the nodes are left to be in the same order produced by
            normal iteration. This makes the resulting graph look ugly.

            + The user can provide a seed value in the settings dictionary to
            help obtain the same result every time the program is run on the
            same input. The user can also change the seed to change the layout
            instead of fiddling around with the DOT code.

            + The components are sorted even though they are then immediately
            shuffled again. This is to ensure the rng.shuffle function produces
            the same result for the same seed.

        Second: The keys and node dictionaries for all of the nodes in all of
        the components are then returned in lexicographical order.
        '''

        components = weakly_connected_components(self.graph)
        components = sorted(components, key = lambda component : min(component, key=str))
        rng = random.Random(self.settings['seed'])
        rng.shuffle(components)

        for component in components:
            for key in sorted(component, key=str):
                yield key, self.graph.node[key]

    def ordered_edges(self):
        '''
        An iterator over this graph's edges and edge dictionaries, in the order
        they should be printed. The edges are sorted first by parent key, then
        child key, then (if necessary) the string form of the edge's attribute
        dictionary.
        '''

        edges = self.graph.edges(data=True)

        # t[0]: parent key
        # t[1]: child key
        # t[2]: edge attribute dictionary
        edges = sorted(edges, key = lambda t : (t[0], t[1], map(str, t[2])))

        yield from edges

class TreeException(Exception):
    pass

