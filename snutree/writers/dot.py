import logging
from snutree import dot
from snutree.errors import SnutreeWriterError
from snutree.tree import TreeEntity
from snutree.logging import logged
from snutree.colors import ColorPicker
from snutree.tree import TreeError
from snutree.cerberus import optional_boolean, nonempty_string, Validator

###############################################################################
###############################################################################
#### Cerberus Schema                                                       ####
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


filetypes = {'pdf', 'dot'}

DOT_SCHEMA = {

        'name' : {
            'regex' : 'dot',
            'nullable' : True,
            },

        'filetype' : {
            'allowed' : list(filetypes),
            },
            
        # Flags
        **{ flag : optional_boolean for flag in [
            'ranks',
            'custom_edges',
            'custom_nodes',
            'no_singletons',
            'colors',
            'unknowns'
            ]},

        # If no_singletons is enabled, any singleton member with a rank higher
        # than this rank will trigger a warning before being dropped
        'warn_rank' : {
            'coerce' : 'optional_rank_type',
            'nullable' : True,
            'default' : None,
            },


        # Default attributes for graphs, nodes, edges, and their subcategories
        'defaults' : {
            'type' : 'dict',
            'default' : {},
            'schema' : {
                'graph' : attribute_defaults('all'),
                'node' : attribute_defaults('all', 'rank', 'unknown', 'member'),
                'edge' : attribute_defaults('all', 'rank', 'unknown'),
                }
            },

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
                        'coerce' : 'rank_type',
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

        }

###############################################################################
###############################################################################
#### Main                                                                  ####
###############################################################################
###############################################################################

def from_FamilyTree(tree, RankType, config):
    '''
    Convert the tree into an object representing a DOT file, then return
    that object.
    '''

    validator = Validator(DOT_SCHEMA, RankType=RankType)
    config = validator.validated(config)

    decorate(tree, config)
    dotgraph = create_dot_graph(tree, config['ranks'], config['defaults'])

    return dotgraph

###############################################################################
###############################################################################
#### Decoration                                                            ####
###############################################################################
###############################################################################

def decorate(tree, config):
    '''
    Add DOT attributes to the nodes and edges in the tree. Also add/remove
    nodes/edges to prepare it for display.
    '''

    # Add DOT attributes
    for node in tree.nodes():
        node['attributes'] = { 'label' : node['entity'].label }
    for edge in tree.edges():
        edge['attributes'] = {}

    # Make structural changes to prepare the tree for display, depending on the
    # values of the flags
    unknown_node_defaults = config['defaults']['node']['unknown']
    unknown_edge_defaults = config['defaults']['edge']['unknown']
    # pylint: disable=expression-not-assigned
    config['custom_nodes'] and add_custom_nodes(tree, config['nodes'])
    config['custom_edges'] and add_custom_edges(tree, config['edges'])
    config['no_singletons'] and remove_singleton_members(tree, config['warn_rank'])
    config['colors'] and add_colors(tree, config['family_colors'])
    config['unknowns'] and add_orphan_parents(tree, unknown_node_defaults, unknown_edge_defaults)

@logged
def add_custom_nodes(tree, nodes):
    '''
    Add the custom nodes to the tree along with associated DOT attributes.
    '''
    for key, value in nodes.items():
        rank = value['rank']
        attributes = value['attributes']
        tree.add_entity(TreeEntity(key, rank=rank), attributes=attributes)

@logged
def add_custom_edges(tree, paths):
    '''
    Add the custom edges (i.e., paths) to the tree along with associated DOT
    attributes. All nodes referenced in these edges must already be defined in
    the tree. "Edges" with more than two nodes can also be added by included
    more in the nodes list.
    '''

    for path in paths:

        # Check node existence
        nodes = path['nodes']
        for key in nodes:
            if key not in tree:
                path_or_edge = 'path' if len(nodes) > 2 else 'edge'
                msg = f'custom {path_or_edge} {nodes} has undefined node: {key!r}'
                raise SnutreeWriterError(msg)

        # Add edges in this path
        attributes = path['attributes']
        edges = [(u, v) for u, v in zip(nodes[:-1], nodes[1:])]
        tree.add_edges(edges, attributes=attributes)

@logged
def remove_singleton_members(tree, warn_rank=None):
    '''
    Remove all members in the tree whose nodes neither have parents nor children.
    '''
    keys = []
    for singleton in tree.singletons():
        key = singleton.key
        keys.append(key)
        rank = singleton.is_ranked() and singleton.rank
        if warn_rank is not None and warn_rank <= rank:
            msg = f'(warn_rank>={warn_rank!r}) singleton {key!r} with rank {rank!r} was dropped '
            logging.getLogger(__name__).warning(msg)
    tree.remove(keys)

@logged
def add_colors(tree, family_colors):
    '''
    Add colors to member nodes, based on their family. Uses the map
    family_colors to determines colors; its keys are node keys and its values
    are Graphviz colors. Any family not in the color map will have a color
    assigned to it automatically. Warns if the family_colors contains a key
    that is not in the tree itself.
    '''

    color_picker = ColorPicker.from_graphviz()

    # Take note of the family-color mappings in family_color
    for key, color in family_colors.items():
        if key not in tree:
            msg = f'family color map includes nonexistent member: {key!r}'
            logging.getLogger(__name__).warning(msg)
            continue
        family = tree[key]['family']
        if 'color' in family:
            msg = f'family of member {key!r} already assigned the color {color!r}'
            raise SnutreeWriterError(msg)
        color_picker.use(color)
        tree[key]['family']['color'] = color

    # Color the nodes. The nodes are sorted first, to ensure that the same
    # colors are used for the same input data when there are families with
    # unassigned colors.
    for key in sorted(tree.keys()):
        node = tree[key]
        family = node.get('family')
        if family is not None:
            if 'color' not in family:
                family['color'] = next(color_picker)
            node['attributes']['color'] = family['color']

@logged
def add_orphan_parents(tree, node_attributes, edge_attributes):
    '''
    Add custom nodes as parents to those members whose nodes currently have no
    parents. Use the parameters to set node and edge attributes for the new
    custom nodes and associated edges.
    '''
    for orphan in tree.orphans():
        parent = UnidentifiedMember(orphan)
        orphan.parent = parent.key
        tree.add_entity(parent, attributes=node_attributes)
        tree.add_edge(orphan.parent, orphan.key, attributes=edge_attributes)

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

###############################################################################
###############################################################################
#### Convert to DOT Graph                                                  ####
###############################################################################
###############################################################################

@logged
def create_dot_graph(tree, ranks, defaults):
    '''
    Use the FamilyTree to create a dot.Graph instance. Set ranks=True to enable
    putting the nodes in rows in order of their rank, instead of making a basic
    tree structure. The defaults dictionary contains default Graphviz
    attributes for various types of items on the graph (see DOT_SCHEMA).
    '''

    members = create_tree_subgraph(tree, 'members', defaults['node']['member'])
    dotgraph = dot.Graph('family_tree', 'digraph', attributes=defaults['graph']['all'])
    node_defaults = dot.Defaults('node', attributes=defaults['node']['all'])
    edge_defaults = dot.Defaults('edge', attributes=defaults['edge']['all'])

    if not ranks:
        dotgraph.children = [node_defaults, edge_defaults, members]
    else:
        min_rank, max_rank = tree.get_rank_bounds()
        max_rank += 1 # always include one extra, blank rank at the end
        node_attributes = defaults['node']['rank']
        edge_attributes = defaults['edge']['rank']
        dates_left = create_date_subgraph(tree, 'L', min_rank, max_rank, node_attributes, edge_attributes)
        dates_right = create_date_subgraph(tree, 'R', min_rank, max_rank, node_attributes, edge_attributes)
        ranks = create_ranks(tree, min_rank, max_rank)
        dotgraph.children = [node_defaults, edge_defaults, dates_left, members, dates_right] + ranks

    return dotgraph

def create_tree_subgraph(tree, subgraph_key, node_defaults):
    '''
    Create and return the DOT subgraph that will contain the member nodes
    and their relationships.
    '''

    dotgraph = dot.Graph(subgraph_key, 'subgraph')
    node_defaults = dot.Defaults('node', node_defaults)

    nodes = []
    for key, node_dict in tree.ordered_items():
        nodes.append(dot.Node(key, node_dict['attributes']))

    edges = []
    for parent_key, child_key, edge_dict in tree.ordered_edges():
        edges.append(dot.Edge(parent_key, child_key, edge_dict['attributes']))

    dotgraph.children = [node_defaults] + nodes + edges

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
        nodes.append(dot.Node(this_rank_key, attributes={'label' : rank}))
        edges.append(dot.Edge(this_rank_key, next_rank_key))
        rank += 1

    nodes.append(dot.Node(f'{rank}{suffix}', attributes={'label' : rank}))

    subgraph.children = [node_defaults, edge_defaults] + nodes + edges

    return subgraph

def create_ranks(tree, min_rank, max_rank):
    '''
    Create and return the DOT ranks.
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

