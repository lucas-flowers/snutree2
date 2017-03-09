import random
import logging
from enum import Enum
from abc import ABCMeta, abstractmethod
from networkx import DiGraph
from networkx.algorithms.components import weakly_connected_components
from cerberus import Validator
from . import dot, SnutreeError
from .utilities import logged, ColorPicker
from .utilities.cerberus import optional_boolean, nonempty_string, semester_like, validate

###############################################################################
###############################################################################
#### Cerberus Schemas                                                      ####
###############################################################################
###############################################################################

# Graphviz attributes
graphviz_attributes = {
        'type' : 'dict',
        'default' : {},
        'valueschema' : {
            'type' : ['string', 'number', 'boolean']
            }
        }

# Contains groups of attributes labeled by the strings in `allowed`
dot_defaults = lambda *allowed : {
        'type' : 'dict',
        'nullable' : False,
        'default' : { a : {} for a in allowed },
        'keyschema' : {
            'allowed' : allowed,
            },
        'valueschema' : graphviz_attributes
        }

###############################################################################
###############################################################################
#### Entities on the Tree                                                  ####
###############################################################################
###############################################################################

class TreeEntity(metaclass=ABCMeta):
    '''

    A node on the Family Tree, whether it be the node of an actual member, a
    rank name, or just decoration.

    Entities should have these fields:

        + key: The key to be used in DOT

        + parent: The key of the entity's parent node

        + _rank: A private field storing a rank ID, which is assumed to be
        some kind of integer-compatible object (e.g., actual integers
        representing years, a Semester object, or other ordered types that
        integers can be added to). This field might be allowed to remain
        unset, though it will raise an error if used before it is set.

        + dot_attributes: The node attributes to be used in DOT

    '''

    def __init__(self, key, rank=None):
        self.key = key
        self._rank = rank

    @property
    def rank(self):
        if self._rank:
            return self._rank
        else:
            msg = 'missing rank value for entity {!r}'
            raise TreeEntityAttributeError(msg.format(self.key))

    @rank.setter
    def rank(self, value):
        self._rank = value

    @property
    def dot_attributes(self):
        return {}

class Custom(TreeEntity):
    '''
    TreeEntities used for decoration.
    '''

    def __init__(self, key, rank=None, attributes=None):
        self.key = key
        self.rank = rank
        self.attributes = attributes or {}

    @property
    def dot_attributes(self):
        return self.attributes

class UnidentifiedMember(Custom):
    '''
    All members are assumed to have parents. If a member does not have a known
    parent. UnidentifiedMembers are given ranks one rank before the members
    they are parents to, unless the rank is unknown, in which case it is left
    null. (Assuming the "unknowns" option is selected.)
    '''

    def __init__(self, member, attributes=None):
        self.key = '{} Parent'.format(member.key)
        try:
            self.rank = member.rank - 1
        except TreeEntityAttributeError:
            self.rank = None
        self.attributes = attributes or {}

class Member(TreeEntity, metaclass=ABCMeta):
    '''
    A member of the organization.
    '''

    @abstractmethod
    def get_dot_label(self):
        pass

    @property
    def dot_attributes(self):
        return {'label' : self.get_dot_label()}

class TreeEntityAttributeError(SnutreeError):
    pass

###############################################################################
###############################################################################
#### Family Tree                                                           ####
###############################################################################
###############################################################################

class FamilyTree:
    '''
    Representation of the family tree. The tree is made of nodes connected by
    edges (duh). Every node must store a TreeEntity object in node['entity'],
    and TreeEntities may either be Members or non-Members. All entities must
    have a valid rank field when the tree is printed (unless ranks are ignored
    in the settings dictionary).

    Members have big-little relationships, determined by the parent field. This
    relationship determines the edges between them. Non-Members do *not* have
    such relationships, though they may have edges in the tree provided from
    outside the directory (either through custom edges or special code).
    '''

    # TODO shouldn't defaults be immutables?

    # Option flag names
    flags = [
            'ranks',
            'custom_edges',
            'custom_nodes',
            'no_singletons',
            'family_colors',
            'unknowns',
            ]

    SETTINGS_VALIDATOR = Validator({

        # Layout options
        'layout' : {
            'type' : 'dict',
            'schema' : { flag : optional_boolean for flag in flags },
            'default' : { flag : True for flag in flags },
            },

        # Default attributes for graphs, nodes, edges, and their subcategories
        'graph_defaults' : dot_defaults('all'),
        'node_defaults' : dot_defaults('all', 'rank', 'unknown', 'member'),
        'edge_defaults' : dot_defaults('all', 'rank', 'unknown'),

        # A mapping of node keys to colors
        'family_colors' : {
            'type' : 'dict',
            'default' : {},
            'keyschema' : nonempty_string,
            'valueschema' : nonempty_string,
            },

        # Custom nodes, each with Graphviz attributes and a rank
        'nodes' : {
            'type' : 'dict',
            'default' : {},
            'keyschema' : nonempty_string,
            'valueschema' : {
                'type' : 'dict',
                'schema' : {
                    'rank' : semester_like, # TODO the type doesn't actually need to be semester
                    'attributes' : graphviz_attributes,
                    }
                }
            },

        # Custom edges: Each entry in the list has a list of nodes, which are
        # used to represent a path from which to create edges (which is why
        # there must be at least two nodes in each list). There are also edge
        # attributes applied to all edges in the path.
        'edges' : {
            'type' : 'list',
            'default' : [],
            'schema' : {
                'type' : 'dict',
                'schema' : {
                    'nodes' : {
                        'type' : 'list',
                        'required' : True,
                        'minlength' : 2,
                        'schema' : nonempty_string,
                        },
                    'attributes' : graphviz_attributes,
                    }
                },
            },

        # Seed for the RNG, to provide consistent output
        'seed': {
                'type' : 'integer',
                'default' : 71,
                }

    })

    @logged
    def __init__(self, members, settings=None):

        self.graph = DiGraph()
        self.settings = validate(self.SETTINGS_VALIDATOR, settings or {})

        # Add all the entities in the settings and member list provided
        self.add_members(members)
        self.add_custom_nodes()

        # Add all the edges in the settings and members provided
        self.add_member_relationships()
        self.add_custom_edges()

        # Decorations
        self.remove_singleton_members()
        self.mark_families()
        self.add_colors()
        self.add_orphan_parents()

    ###########################################################################
    #### Utilities                                                         ####
    ###########################################################################

    class option:
        '''
        Decorates methods that can be toggled through options in the tree's
        settings dictionary. For example, @option('custom_edges') will enable
        the function it decorates if the 'custom_edges' option in the
        settings dictionary is True---and disable it otherwise.
        '''

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
        '''
        Returns a subgraph consisting only of members.
        '''
        member_keys = (k for k, m in self.nodes_iter('entity') if isinstance(m, Member))
        return self.graph.subgraph(member_keys)

    def orphan_keys(self):
        '''
        Returns the keys of all orphaned members in the tree.
        '''
        in_degrees = self.graph.in_degree().items()
        return (k for k, in_degree in in_degrees if in_degree == 0
                and isinstance(self.graph.node[k]['entity'], Member))

    def add_entity(self, entity):
        '''
        Add the TreeEntity to the tree, catching any duplicates.
        '''

        key = entity.key
        if key in self.graph:
            code = TreeErrorCode.DUPLICATE_ENTITY
            msg = 'duplicate entity key: {!r}'
            raise TreeError(code, msg.format(key))
        self.graph.add_node(key, entity=entity, dot_attributes=entity.dot_attributes)

    def add_big_relationship(self, member, dot_attributes=None):
        '''
        Add an edge for the member and its parent to the tree, with any
        provided DOT edge attributes. Ensure that the parent actually exists in
        the tree already and that the parent is on the same rank or on a rank
        before the member.
        '''

        ckey = member.key
        pkey = member.parent

        if pkey not in self.graph:
            code = TreeErrorCode.PARENT_UNKNOWN
            msg = 'member {!r} has unknown parent: {!r}'
            raise TreeError(code, msg.format(ckey, pkey))

        parent = self.graph.node[pkey]['entity']

        if self.settings['layout']['ranks'] and member.rank < parent.rank:
            code = TreeErrorCode.PARENT_NOT_PRIOR
            msg = 'rank {!r} of member {!r} cannot be prior to rank of parent {!r}: {!r}'
            vals = member.rank, ckey, pkey, parent.rank
            raise TreeError(code, msg.format(*vals))

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

    @logged
    def add_member_relationships(self):
        '''
        Connect all Members in the tree, based on the value of their parent
        field, by adding the edge (parent, member). Parents must also be
        Members (to add non-Members as parent nodes, use custom edges).
        '''

        for _, entity in self.nodes_iter('entity'):
            if isinstance(entity, Member) and entity.parent:
                self.add_big_relationship(entity)

    @option('custom_edges')
    @logged
    def add_custom_edges(self):
        '''
        Add all custom edges loaded from settings. All nodes in the edge list m
        '''

        for path in self.settings['edges']:

            nodes = path['nodes']
            for key in nodes:
                if key not in self.graph:
                    path_type = 'path' if len(nodes) > 2 else 'edge'
                    code = TreeErrorCode.UNKNOWN_EDGE_COMPONENT
                    msg = 'custom {} {!r} has undefined node: {!r}'
                    vals = path_type, path['nodes'], key
                    raise TreeError(code, msg.format(*vals))

            attributes = path['attributes']

            edges = [(u, v) for u, v in zip(nodes[:-1], nodes[1:])]
            self.graph.add_edges_from(edges, dot_attributes=attributes)

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
        '''
        Mark all families in the tree by adding a 'family' attribute to each
        Member node, containing the key of the family's root.
        '''

        # Families are weakly connected components of the members-only graph
        members_only = self.member_subgraph()
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
        many singletons do not have well-formed pledge class rank values in the
        actual Sigma Nu directory directory (and determining pledge class
        semesters values accurately is not simple enough for me to bother
        doing). If every pledge class semester filled in, this could occur
        before add_edges and we can remove some of the extra code in this
        function that would normally be done by add_XXX_attributes.
        '''

        for orphan_key in self.orphan_keys():

            orphan = self.graph.node[orphan_key]['entity']

            parent = UnidentifiedMember(orphan, self.settings['node_defaults']['unknown'])

            orphan.parent = parent.key
            self.add_entity(parent)
            self.graph.add_edge(orphan.parent, orphan_key, dot_attributes=self.settings['edge_defaults']['unknown'])

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
        color_picker = ColorPicker.from_graphviz()

        for key, color in family_colors.items():

            if key not in self.graph.node:
                msg = 'warning: family color map includes nonexistent member: {!r}'
                logging.warning(msg.format(key))

            else:

                family = self.graph.node[key]['family']
                if 'color' in family:
                    code = TreeErrorCode.FAMILY_COLOR_CONFLICT
                    msg = 'family of member {!r} already assigned the color {!r}'
                    raise TreeError(code, msg.format(key, color))

                color_picker.use(color)
                self.graph.node[key]['family']['color'] = color

        # The nodes are sorted first, to ensure that the same colors are used
        # for the same input data.
        for key, node_dict in sorted(self.graph.nodes_iter(data=True)):
            if isinstance(node_dict['entity'], Member):
                family_dict = node_dict['family']
                if 'color' not in family_dict:
                    family_dict['color'] = next(color_picker)

                node_dict['dot_attributes']['color'] = family_dict['color']

    @logged
    def to_dot_graph(self):
        '''
        Convert the tree into an object representing a DOT file, then return
        that object.
        '''

        tree = self.create_tree_subgraph('members')

        graph_defaults = self.settings['graph_defaults']['all']
        dotgraph = dot.Graph('family_tree', 'digraph', attributes=graph_defaults)

        node_defaults = dot.Defaults('node', self.settings['node_defaults']['all'])
        edge_defaults = dot.Defaults('edge', self.settings['edge_defaults']['all'])

        if self.settings['layout']['ranks']:
            min_rank, max_rank = self.get_rank_bounds()
            max_rank += 1 # always include one extra, blank rank at the end
            dates_left = self.create_date_subgraph('L', min_rank, max_rank)
            dates_right = self.create_date_subgraph('R', min_rank, max_rank)
            ranks = self.create_ranks(min_rank, max_rank)
            dotgraph.children = [node_defaults, edge_defaults, dates_left, tree, dates_right] + ranks

        else:
            dotgraph.children = [node_defaults, edge_defaults, tree]

        return dotgraph

    def get_rank_bounds(self):
        '''
        Find and return the values of the highest and lowest ranks in use.
        '''

        min_rank, max_rank = float('inf'), float('-inf')
        for _, entity in self.nodes_iter('entity'):
            rank = entity.rank
            if rank and min_rank > rank:
                min_rank = rank
            if rank and max_rank < rank:
                max_rank = rank
        return min_rank, max_rank

    def create_date_subgraph(self, key, min_rank, max_rank):
        '''
        Return a DOT subgraph containing the labels for each rank. The `key`
        variable adds an additional identifier for the subgraph and its rank
        labels.
        '''

        subgraph = dot.Graph('dates{}'.format(key), 'subgraph')

        node_defaults = dot.Defaults('node', self.settings['node_defaults']['rank'])
        edge_defaults = dot.Defaults('edge', self.settings['edge_defaults']['rank'])

        nodes = []
        edges = []
        rank = min_rank
        while rank < max_rank:
            this_rank_key = '{}{}'.format(rank, key)
            next_rank_key = '{}{}'.format(rank+1, key)
            nodes.append(dot.Node(this_rank_key, {'label' : rank}))
            edges.append(dot.Edge(this_rank_key, next_rank_key))
            rank += 1

        this_rank_key = '{}{}'.format(rank, key)
        nodes.append(dot.Node(this_rank_key, {'label' : rank}))

        subgraph.children = [node_defaults, edge_defaults] + nodes + edges

        return subgraph

    def create_tree_subgraph(self, key):
        '''
        Create and return the DOT subgraph that will contain the member nodes
        and their relationships.
        '''

        dotgraph = dot.Graph(key, 'subgraph')

        node_defaults = dot.Defaults('node', self.settings['node_defaults']['member'])

        nodes = []
        for key, node_dict in self.ordered_nodes():
            nodes.append(dot.Node(key, node_dict['dot_attributes']))

        edges = []
        for parent_key, child_key, edge_dict in self.ordered_edges():
            edges.append(dot.Edge(parent_key, child_key, edge_dict['dot_attributes']))

        dotgraph.children = [node_defaults] + nodes + edges

        return dotgraph

    def create_ranks(self, min_rank, max_rank):
        '''
        Create and return the DOT ranks
        '''

        # `while` instead of `range` because ranks might not be true integers
        ranks = []
        i = min_rank
        while i < max_rank:
            ranks.append(dot.Rank([f'{i}L', f'{i}R']))
            i += 1

        for key, entity in self.nodes_iter('entity'):
            ranks[entity.rank - min_rank].keys.append(key)

        return ranks

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

        def sort_key(arg):
            parent_key, child_key, edge_dict = arg
            return (parent_key, child_key, str(edge_dict))

        yield from sorted(edges, key=sort_key)

###############################################################################
###############################################################################
#### Errors                                                                ####
###############################################################################
###############################################################################

class TreeError(SnutreeError):
    '''
    Raised after any tree-related errors occur. The errno should be filled with
    one of the TreeErrorCodes, which makes testing errors easier.
    '''

    def __init__(self, errno, msg=None):
        self.errno = errno
        self.message = msg

    def __str__(self):
        return self.message

TreeErrorCode = Enum('TreeErrorCode', (
        'DUPLICATE_ENTITY',
        'PARENT_UNKNOWN',
        'PARENT_NOT_PRIOR',
        'UNKNOWN_EDGE_COMPONENT',
        'FAMILY_COLOR_CONFLICT',
        ))

