import random
import networkx as nx
from collections import deque
from networkx.algorithms.components import weakly_connected_components
from networkx.algorithms.cycles import find_cycle
from networkx.exception import NetworkXNoCycle
from . import dot
from .semester import semester_range
from .entity import Member, Custom, UnidentifiedInitiate, Initiate
from .utilities import logged

class FamilyTree:
    '''
    Representation of the family tree. The tree is made of nodes connected by
    edges (duh). Every node must store a TreeEntity object in node['entity'],
    and TreeEntities may either be Members or non-Members. All entities must
    have a valid semester field when the tree is printed (unless semesters are
    ignored in the settings dictionary).

    Members have big-little relationships, determined by the parent field. This
    relationship determines the edges between them. Non-members do *not* have
    such relationships, though they may have edges in the tree provided from
    outside the directory (either through custom edges or special code).
    '''

    def __init__(self, directory, settings=None):

        self.graph = nx.DiGraph()
        self.settings = settings or {}

        # Add all the entities in the settings and directory provided
        self.add_members(directory.get_members())
        self.add_custom_nodes()

        # Add all the edges in the settings and members provided
        self.add_member_relationships()
        self.add_custom_edges()

        self.remove_singleton_members()
        self.mark_families()
        self.add_colors()
        self.add_orphan_parents()

    ###########################################################################
    #### Utilities                                                         ####
    ###########################################################################

    class option:
        def __init__(self, option_name):
            self.option_name = option_name
        def __call__(self, function):
            def wrapped(tree_self):
                if tree_self.settings['layout'][self.option_name]:
                    function(tree_self)
            return wrapped

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

    def member_subgraph(self):
        return self.graph.subgraph([
            key for key, node_dict in self.graph.nodes_iter(data=True)
            if isinstance(node_dict['entity'], Member)
            ])

    def add_entity(self, entity):

        key = entity.get_key()
        if key in self.graph:
            msg = 'duplicate entity key: {!r}'
            raise TreeError(msg.format(key))
        self.graph.add_node(key, entity=entity, dot_attributes=entity.dot_attributes())

    def add_big_relationship(self, member, dot_attributes=None):

        ckey = member.get_key()
        pkey = member.parent

        if pkey not in self.graph:
            msg = 'member {!r} has unknown parent: {!r}'
            raise TreeError(msg.format(ckey, pkey))

        parent = self.graph.node[pkey]['entity']

        if not isinstance(parent, Initiate):
            msg = 'big brother of {!r} must be an initiated member: {!r}'
            raise TreeError(msg.format(ckey, pkey))
        elif self.settings['layout']['semesters'] and member.semester < parent.semester:
            msg = 'semester {!r} of member {!r} cannot be prior to semester of big brother {!r}: {!r}'
            vals = member.semester, ckey, pkey, parent.semester
            raise TreeError(msg.format(*vals))
        else:
            self.graph.add_edge(pkey, ckey, dot_attributes=dot_attributes or {})

    ###########################################################################
    #### Decoration                                                        ####
    ###########################################################################

    @logged
    def add_members(self, member_list):
        '''
        Add the members to the graph.
        '''

        for member in member_list:
            self.add_entity(member)

    @option('custom_nodes')
    @logged
    def add_custom_nodes(self):
        '''
        Add all custom nodes loaded from settings.
        '''

        for key, value in self.settings['nodes'].items():
            self.add_entity(Custom(key, **value))

    @option('custom_edges')
    @logged
    def add_custom_edges(self):
        '''
        Add all custom edges loaded from settings.
        '''

        for path in self.settings['edges']:

            nodes = path['nodes']
            for key in nodes:
                if key not in self.graph:
                    path_type = 'path' if len(nodes) > 2 else 'edge'
                    msg = 'custom {} {!r} has undefined node: {!r}'
                    vals = path_type, path['nodes'], key
                    raise TreeError(msg.format(*vals))
            attributes = path['attributes']

            edges = [(u, v) for u, v in zip(nodes[:-1], nodes[1:])]
            self.graph.add_edges_from(edges, dot_attributes=attributes)

    @logged
    def add_member_relationships(self):
        '''
        Connect all Members in the tree, based on the value of their parent
        field, by adding the edge (parent, member). Parents must also be
        Members (to add non-Members as parent nodes, use custom edges).
        '''

        for key, entity in self.nodes_iter('entity'):
            if isinstance(entity, Member) and entity.parent:
                self.add_big_relationship(entity)

        # There must be no cycles in the tree of members
        try:
            cycle_edges = find_cycle(self.member_subgraph(), orientation='ignore')
            msg = 'found unexpected cycle in big-little relationships: {!r}'
            raise TreeError(msg.format(cycle_edges))
        except NetworkXNoCycle:
            pass

    @option('no_singletons')
    @logged
    def remove_singleton_members(self):
        '''
        Remove all members in the tree whose nodes neither have parents nor
        children, as determined by the node's degree (including both in-edges
        and out-edges).
        '''

        # TODO protect singletons (e.g., refounders without littles) after a
        # certain date so they don't disappear without at least a warning?
        singletons = [key for key, degree in self.graph.degree_iter() if degree == 0
                and isinstance(self.graph.node[key]['entity'], Member)]

        self.graph.remove_nodes_from(singletons)

    @option('family_colors')
    @logged
    def mark_families(self):

        # Members-only graph
        members_only = self.graph.subgraph(
                [key for key, member in self.nodes_iter('entity')
                    if isinstance(member, Member)]
                )

        # Families are weakly connected components of the members-only graph
        families = weakly_connected_components(members_only)

        # Add a pointer to each member's family subgraph
        for family in families:
            family_dict = {}
            for key in family:
                self.graph.node[key]['family'] = family_dict

    @option('unknowns')
    @logged
    def add_orphan_parents(self):
        '''
        Add custom entities as parents to members whose nodes have no parents,
        as determined by the nodes' in-degrees.

        Note: This must occur after edges are generated in order to determine
        degrees. But it must also occur after singletons are removed, because
        many singletons do not have well-formed pledge class semester values in
        the directory (and determining pledge class semester values accurately
        is not simple enough for me to bother doing). If every pledge class
        semesters were filled in, this could occur before add_edges and we can
        remove some of the extra code in this function that would normally be
        done by add_XXX_attributes.
        '''

        orphan_keys = [key
                for key, in_degree
                in self.graph.in_degree().items()
                if in_degree == 0
                and isinstance(self.graph.node[key]['entity'], Member)
                ]

        for orphan_key in orphan_keys:

            orphan = self.graph.node[orphan_key]['entity']

            parent = UnidentifiedInitiate(orphan,
                    self.settings['node_defaults']['unknown'])

            # Set orphan parent
            orphan.parent = parent.get_key()

            self.add_entity(parent)
            self.graph.add_edge(orphan.parent, orphan_key,
                    dot_attributes=self.settings['edge_defaults']['unknown'])

    ###########################################################################
    #### Convert to DOT                                                    ####
    ###########################################################################

    @option('family_colors')
    @logged
    def add_colors(self):
        '''
        Add colors to member nodes, based on their family. Uses settings
        dictionary to provide initial colors, and generates the rest as needed.
        '''

        family_colors = self.settings['family_colors']
        other_colors = graphviz_colors()

        for key, color in family_colors.items():

            if key not in self.graph.node:
                print('warning: family color map includes nonexistent member: {!r}'
                        .format(key))

            else:

                # Add the used color to the end and remove the first instance of it
                other_colors.append(color)
                other_colors.remove(color)

                family = self.graph.node[key]['family']
                if 'color' in family:
                    msg = 'family of member {!r} already assigned the color {!r}'
                    raise TreeError(msg.format(key, color))

                # Add the used color to the end and remove the first instance of it
                other_colors.append(color)
                other_colors.remove(color)

                self.graph.node[key]['family']['color'] = color

        # The nodes are sorted first, to ensure that the same colors are used
        # for the same input data.
        for key, node_dict in sorted(self.graph.nodes_iter(data=True)):
            if isinstance(node_dict['entity'], Member):
                family_dict = node_dict['family']
                if 'color' not in family_dict:

                    # Pop a color, save it, and move it to deque's other end
                    color = other_colors.popleft()
                    other_colors.append(color)

                    family_dict['color'] = color

                node_dict['dot_attributes']['color'] = family_dict['color']

    @logged
    def to_dot_graph(self):

        tree = self.create_tree_subgraph('members')

        dotgraph = dot.Graph(
                'family_tree',
                'digraph',
                attributes=self.settings['graph_defaults']['all'],
                )

        node_defaults = dot.Defaults('node', self.settings['node_defaults']['all'])
        edge_defaults = dot.Defaults('edge', self.settings['edge_defaults']['all'])

        if self.settings['layout']['semesters']:
            min_semester, max_semester = self.get_semester_bounds()
            dates_left = self.create_date_subgraph('L', min_semester, max_semester)
            dates_right = self.create_date_subgraph('R', min_semester, max_semester)
            ranks = self.create_ranks()
            dotgraph.children = \
                    [node_defaults, edge_defaults, dates_left, tree, dates_right] + ranks

        else:
            dotgraph.children = [node_defaults, edge_defaults, tree]

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
                )

        node_defaults = dot.Defaults('node', self.settings['node_defaults']['semester'])
        edge_defaults = dot.Defaults('edge', self.settings['edge_defaults']['semester'])

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

        subgraph.children = [node_defaults, edge_defaults] + nodes + edges

        return subgraph

    def create_tree_subgraph(self, key):

        dotgraph = dot.Graph(
                key,
                'subgraph',
                )

        node_defaults = dot.Defaults('node', self.settings['node_defaults']['member'])

        nodes = []
        for key, node_dict in self.ordered_nodes():
            nodes.append(dot.Node(key, node_dict['dot_attributes']))

        edges = []
        for parent_key, child_key, edge_dict in self.ordered_edges():
            edges.append(dot.Edge(parent_key, child_key, edge_dict['dot_attributes']))

        dotgraph.children = [node_defaults] + nodes + edges

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

class TreeError(Exception):
    pass

def graphviz_colors():
    return deque([
            'limegreen',
            'tan3',
            'brown4',
            'plum3',
            'chartreuse1',
            'deeppink3',
            'paleturquoise4',
            'navy',
            'darkseagreen3',
            'darkslategray',
            'plum1',
            'deepskyblue3',
            'dodgerblue1',
            'slategray2',
            'salmon2',
            'violetred3',
            'azure4',
            'indigo',
            'thistle3',
            'darkorange1',
            'deepskyblue1',
            'lavenderblush3',
            'slategray',
            'purple2',
            'peachpuff',
            'palegreen4',
            'pink3',
            'burlywood3',
            'wheat4',
            'mediumspringgreen',
            'palegreen3',
            'blueviolet',
            'ivory4',
            'cadetblue4',
            'maroon2',
            'orangered',
            'goldenrod3',
            'olivedrab1',
            'slategrey',
            'gold3',
            'goldenrod2',
            'mediumorchid4',
            'mediumseagreen',
            'mistyrose2',
            'magenta2',
            'khaki',
            'cadetblue',
            'firebrick4',
            'palegreen',
            'deepskyblue',
            'cadetblue2',
            'gold1',
            'firebrick1',
            'turquoise1',
            'coral4',
            'purple1',
            'hotpink2',
            'paleturquoise2',
            'brown2',
            'darkolivegreen',
            'orange2',
            'orange1',
            'indianred1',
            'deepskyblue2',
            'royalblue2',
            'bisque4',
            'darkolivegreen4',
            'dodgerblue4',
            'chocolate',
            'darkolivegreen3',
            'gold',
            'thistle1',
            'blue4',
            'salmon3',
            'sienna4',
            'forestgreen',
            'salmon',
            'indianred3',
            'burlywood',
            'rosybrown',
            'darkgoldenrod',
            'skyblue4',
            'indianred',
            'darksalmon',
            'cyan3',
            'deeppink1',
            'ivory1',
            'orangered3',
            'rosybrown1',
            'palevioletred',
            'blanchedalmond',
            'snow3',
            'red1',
            'cyan2',
            'mediumblue',
            'lawngreen',
            'pink4',
            'darkgoldenrod4',
            'lemonchiffon1',
            'pink1',
            'peachpuff2',
            'orangered4',
            'firebrick3',
            'peru',
            'steelblue4',
            'tomato4',
            'oldlace',
            'magenta3',
            'darkorchid3',
            'wheat1',
            'deeppink2',
            'purple3',
            'snow1',
            'mistyrose3',
            'chocolate2',
            'orangered2',
            'pink',
            'darkturquoise',
            'gold2',
            'mistyrose4',
            'snow',
            'slateblue3',
            'firebrick2',
            'darkgreen',
            'turquoise4',
            'indianred2',
            'moccasin',
            'blue2',
            'lemonchiffon3',
            'darkseagreen',
            'springgreen1',
            'mistyrose1',
            'coral1',
            'springgreen',
            'maroon',
            'yellow4',
            'orange3',
            'magenta1',
            'lavenderblush',
            'aquamarine1',
            'brown',
            'blue',
            'turquoise3',
            'cadetblue1',
            'dodgerblue2',
            'khaki1',
            'violetred2',
            'ivory',
            'red4',
            'chartreuse4',
            'tan2',
            'maroon1',
            'royalblue4',
            'springgreen2',
            'darkorange2',
            'steelblue',
            'mediumvioletred',
            'royalblue3',
            'darkseagreen4',
            'olivedrab',
            'blue1',
            'khaki3',
            'cornsilk3',
            'hotpink3',
            'darkslateblue',
            'springgreen4',
            'mintcream',
            'violet',
            'aquamarine3',
            'mediumpurple',
            'purple4',
            'slategray1',
            'black',
            'darkorange',
            'azure2',
            'cyan1',
            'seagreen3',
            'chocolate1',
            'palevioletred3',
            'khaki4',
            'steelblue3',
            'peachpuff1',
            'tan',
            'rosybrown2',
            'seagreen4',
            'steelblue2',
            'thistle2',
            'burlywood4',
            'mediumorchid',
            'skyblue2',
            'violetred',
            'darkorange4',
            'azure',
            'orchid1',
            'maroon3',
            'red',
            'darkgoldenrod3',
            'wheat2',
            'steelblue1',
            'mistyrose',
            'brown1',
            'darkslategray4',
            'mediumpurple1',
            'darkgoldenrod1',
            'bisque',
            'rosybrown3',
            'paleturquoise',
            'sienna1',
            'palegreen1',
            'darkslategray2',
            'slategray4',
            'slategray3',
            'slateblue',
            'cornsilk4',
            'slateblue1',
            'darkolivegreen2',
            'darkolivegreen1',
            'invis',
            'coral2',
            'snow4',
            'springgreen3',
            'darkgoldenrod2',
            'darkseagreen1',
            'lemonchiffon2',
            'red3',
            'ivory3',
            'royalblue',
            'olivedrab3',
            'hotpink',
            'orchid',
            'gainsboro',
            'lemonchiffon4',
            'aliceblue',
            'saddlebrown',
            'plum2',
            'orchid3',
            'cornsilk',
            'midnightblue',
            'darkorchid1',
            'royalblue1',
            'mediumpurple4',
            'deepskyblue4',
            'snow2',
            'aquamarine2',
            'lemonchiffon',
            'rosybrown4',
            'aquamarine4',
            'lavenderblush2',
            'peachpuff4',
            'hotpink4',
            'mediumpurple2',
            'bisque1',
            'tomato',
            'violetred4',
            'firebrick',
            'cyan4',
            'dodgerblue',
            'palevioletred1',
            'linen',
            'wheat3',
            'chartreuse3',
            'yellowgreen',
            'mediumpurple3',
            'darkslategrey',
            'maroon4',
            'cornsilk2',
            'deeppink4',
            'mediumorchid3',
            'paleturquoise3',
            'plum4',
            'khaki2',
            'orchid4',
            'navyblue',
            'paleturquoise1',
            'seagreen1',
            'salmon1',
            'purple',
            'tomato2',
            'chartreuse2',
            'skyblue',
            'ivory2',
            'violetred1',
            'skyblue3',
            'azure3',
            'turquoise2',
            'orangered1',
            'lavender',
            'coral3',
            'darkorchid',
            'gold4',
            'blue3',
            'palevioletred2',
            'goldenrod4',
            'goldenrod',
            'cornsilk1',
            'magenta',
            'olivedrab4',
            'yellow1',
            'slateblue4',
            'mediumorchid2',
            'dimgray',
            'cadetblue3',
            'olivedrab2',
            'plum',
            'deeppink',
            'thistle',
            'peachpuff3',
            'pink2',
            'sienna2',
            'chocolate4',
            'coral',
            'brown3',
            'red2',
            'orchid2',
            'dimgrey',
            'tomato1',
            'darkslategray1',
            'orange4',
            'darkseagreen2',
            'burlywood1',
            'bisque3',
            'crimson',
            'yellow3',
            'hotpink1',
            'darkkhaki',
            'salmon4',
            'mediumaquamarine',
            'seagreen2',
            'bisque2',
            'dodgerblue3',
            'thistle4',
            'powderblue',
            'mediumorchid1',
            'mediumslateblue',
            'tan4',
            'darkslategray3',
            'sandybrown',
            'lavenderblush1',
            'cornflowerblue',
            'aquamarine',
            'tan1',
            'yellow2',
            'goldenrod1',
            'turquoise',
            'darkviolet',
            'tomato3',
            'sienna',
            'wheat',
            'cyan',
            'darkorange3',
            'azure1',
            'sienna3',
            'palevioletred4',
            'darkorchid4',
            'slateblue2',
            'skyblue1',
            'darkorchid2',
            'magenta4',
            'lavenderblush4',
            'seagreen',
            'yellow',
            'palegoldenrod',
            'burlywood2',
            'chartreuse',
            'indianred4',
            'chocolate3',
            'orange',
            'mediumturquoise',
            'palegreen2',
            ])


