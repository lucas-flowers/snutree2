import logging
from snutree import dot
from snutree.errors import SnutreeWriterError
from snutree.tree import TreeEntity, Member
from snutree.logging import logged
from snutree.colors import ColorPicker
from snutree.tree import TreeError
from ..cerberus import optional_boolean, nonempty_string, Validator

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
attribute_defaults = lambda *allowed : {
        'type' : 'dict',
        'nullable' : False,
        'default' : { a : {} for a in allowed },
        'keyschema' : { 'allowed' : allowed },
        'valueschema' : {
            'type' : 'dict',
            }
        }

# Option flag names
flags = [
        'ranks',
        'custom_edges',
        'custom_nodes',
        'no_singletons',
        'family_colors',
        'unknowns',
        ]

def create_settings_validator(RankType):
    '''
    Returns new validator for family tree settings which uses RankType to
    validate the type of rank values.
    '''

    return Validator({

        # Layout options
        'layout' : {
            'type' : 'dict',
            'schema' : { flag : optional_boolean for flag in flags },
            'default' : { flag : True for flag in flags },
            },

        # Default attributes for graphs, nodes, edges, and their subcategories
        'graph_defaults' : attribute_defaults('all'),
        'node_defaults' : attribute_defaults('all', 'rank', 'unknown', 'member'),
        'edge_defaults' : attribute_defaults('all', 'rank', 'unknown'),

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
                    'rank' : {
                        'coerce' : RankType
                        },
                    'attributes' : {
                        'type' : 'dict',
                        'default' : {},
                        }
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
                    'attributes' : {
                        'type' : 'dict',
                        'default' : {},
                        }
                    }
                },
            },

        })

class UnidentifiedMember(TreeEntity):
    '''
    All members are assumed to have parents. If a member does not have a known
    parent. UnidentifiedMembers are given ranks one rank before the members
    they are parents to, unless the rank is unknown, in which case it is left
    null. (Assuming the "unknowns" option is selected.)
    '''

    def __init__(self, member):
        key = f'{member.key} Parent'
        try:
            rank = member.rank - 1
        except TreeError:
            rank = None
        super().__init__(key, rank=rank)


@logged
def add_custom_nodes(tree, nodes):
    '''
    Add all custom nodes loaded from settings.
    '''

    for key, value in nodes.items():
        rank = value['rank']
        attributes = value['attributes']
        tree.add_entity(TreeEntity(key, rank=rank), attributes=attributes)

@logged
def add_custom_edges(tree, edges):
    '''
    Add all custom edges loaded from settings. All nodes in the edge list m
    '''

    for path in edges:

        nodes = path['nodes']
        for key in nodes:
            if key not in tree:
                path_or_edge = 'path' if len(nodes) > 2 else 'edge'
                msg = f'custom {path_or_edge} {nodes} has undefined node: {key!r}'
                raise SnutreeWriterError(msg)

        attributes = path['attributes']

        edges = [(u, v) for u, v in zip(nodes[:-1], nodes[1:])]
        tree.graph.add_edges_from(edges, attributes=attributes)

def add_attributes(tree):

    for node in tree.nodes():
        node['attributes'] = { 'label' : node['entity'].label } 

    for edge in tree.edges():
        edge['attributes'] = {}

@logged
def add_colors(tree, family_colors):
    '''
    Add colors to member nodes, based on their family. Uses settings
    dictionary to provide initial colors, and generates the rest as needed.
    '''

    color_picker = ColorPicker.from_graphviz()

    for key, color in family_colors.items():

        if key not in tree:
            msg = f'family color map includes nonexistent member: {key!r}'
            logging.getLogger(__name__).warning(msg)

        else:

            family = tree[key]['family']
            if 'color' in family:
                msg = f'family of member {key!r} already assigned the color {color!r}'
                raise SnutreeWriterError(msg)

            color_picker.use(color)
            tree[key]['family']['color'] = color

    # The nodes are sorted first, to ensure that the same colors are used
    # for the same input data.
    for key, node_dict in sorted(tree.items(), key=lambda x : x[0]):
        family_dict = node_dict.get('family')
        if family_dict is not None:
            if 'color' not in family_dict:
                family_dict['color'] = next(color_picker)

            node_dict['attributes']['color'] = family_dict['color']

@logged
def add_orphan_parents(tree, node_attributes, edge_attributes):
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

    for orphan in tree.orphans():

        parent = UnidentifiedMember(orphan)

        orphan.parent = parent.key
        tree.add_entity(parent, attributes=node_attributes)
        tree.graph.add_edge(orphan.parent, orphan.key, attributes=edge_attributes)

@logged
def remove_singleton_members(tree):
    '''
    Remove all members in the tree whose nodes neither have parents nor
    children, as determined by the node's degree (including both in-edges
    and out-edges).
    '''

    # TODO protect singletons (e.g., refounders without littles) after a
    # certain date so they don't disappear without at least a warning?

    keys = (singleton.key for singleton in tree.singletons())
    tree.graph.remove_nodes_from(keys)

@logged
def to_dot_graph(tree, RankType, config):
    '''
    Convert the tree into an object representing a DOT file, then return
    that object.
    '''

    config = create_settings_validator(RankType).validated(config)

    add_attributes(tree)

    if config['layout']['custom_nodes']:
        add_custom_nodes(tree, config['nodes'])

    if config['layout']['custom_edges']:
        add_custom_edges(tree, config['edges'])

    if config['layout']['no_singletons']:
        remove_singleton_members(tree)
# ginlee tons

    # TODO move
    if config['layout']['family_colors']:
        add_colors(tree, config['family_colors'])

    if config['layout']['unknowns']:
        node_attributes = config['node_defaults']['unknown']
        edge_attributes = config['edge_defaults']['unknown']
        add_orphan_parents(tree, node_attributes, edge_attributes)

    members = create_tree_subgraph(tree, 'members', config['node_defaults']['member'])

    graph_defaults = config['graph_defaults']['all']
    dotgraph = dot.Graph('family_tree', 'digraph', attributes=graph_defaults)

    node_defaults = dot.Defaults('node', config['node_defaults']['all'])
    edge_defaults = dot.Defaults('edge', config['edge_defaults']['all'])

    if config['layout']['ranks']:
        min_rank, max_rank = tree.get_rank_bounds()
        max_rank += 1 # always include one extra, blank rank at the end
        node_attributes = config['node_defaults']['rank']
        edge_attributes = config['edge_defaults']['rank']
        dates_left = create_date_subgraph(tree, 'L', min_rank, max_rank, node_attributes, edge_attributes)
        dates_right = create_date_subgraph(tree, 'R', min_rank, max_rank, node_attributes, edge_attributes)
        ranks = create_ranks(tree, min_rank, max_rank)
        dotgraph.children = [node_defaults, edge_defaults, dates_left, members, dates_right] + ranks

    else:
        dotgraph.children = [node_defaults, edge_defaults, members]

    return dotgraph

def create_date_subgraph(tree, suffix, min_rank, max_rank, node_defaults, edge_defaults):
    '''
    Return a DOT subgraph containing the labels for each rank. The `suffix`
    is appended to the end of the keys of the subgraph's labels, so more
    than one subgraph can be made, using different suffixes.
    '''

    subgraph = dot.Graph(f'dates{suffix}', 'subgraph')

    node_defaults = dot.Defaults('node', node_defaults)
    edge_defaults = dot.Defaults('edge', edge_defaults)

    nodes, edges = [], []
    rank = min_rank
    while rank < max_rank:
        this_rank_key = f'{rank}{suffix}'
        next_rank_key = f'{rank+1}{suffix}'
        nodes.append(dot.Node(this_rank_key, {'label' : rank}))
        edges.append(dot.Edge(this_rank_key, next_rank_key))
        rank += 1

    nodes.append(dot.Node(f'{rank}{suffix}', {'label' : rank}))

    subgraph.children = [node_defaults, edge_defaults] + nodes + edges

    return subgraph

def create_tree_subgraph(tree, subgraph_key, node_defaults):
    '''
    Create and return the DOT subgraph that will contain the member nodes
    and their relationships.
    '''

    dotgraph = dot.Graph(subgraph_key, 'subgraph')

    node_defaults = dot.Defaults('node', node_defaults)

    nodes = []
    for key, node_dict in tree.ordered_nodes():
        nodes.append(dot.Node(key, node_dict['attributes'])) # TODO validate later

    edges = []
    for parent_key, child_key, edge_dict in tree.ordered_edges():
        edges.append(dot.Edge(parent_key, child_key, edge_dict['attributes'])) # TODO validate later

    dotgraph.children = [node_defaults] + nodes + edges

    return dotgraph

def create_ranks(tree, min_rank, max_rank):
    '''
    Create and return the DOT ranks
    '''

    # `while` instead of `range` because ranks might not be true integers
    ranks = []
    i = min_rank
    while i < max_rank:
        ranks.append(dot.Rank([f'{i}L', f'{i}R']))
        i += 1

    for key, node in tree.items():
        ranks[node['entity'].rank - min_rank].keys.append(key)

    return ranks

