import logging
import sys
import subprocess
from snutree.errors import SnutreeWriterError
from snutree.tree import TreeEntity
from snutree.tree import TreeError
from snutree.utilities import dot
from snutree.utilities.cerberus import Validator
from snutree.utilities.logging import logged
from snutree.utilities.colors import ColorPicker

logger_name = 'snutree.writers.dot'

###############################################################################
###############################################################################
#### API                                                                   ####
###############################################################################
###############################################################################

filetypes = {
        'dot', # Printed directly
        'eps',
        'svg',
        'pdf',
        }

def compile_tree(tree, RankType, config):

    logger = logging.getLogger(logger_name)

    validator = Validator(CONFIG_SCHEMA, RankType=RankType)
    config = validator.validated(config)

    logger.info('Converting to DOT format')
    decorate(tree, config)
    dot_graph = create_dot_graph(tree, config['ranks'], config['defaults'])
    dot_source = dot_graph.to_dot()

    filetype = config["filetype"]
    logger.info('Compiling to {filetype}'.format(filetype=filetype))
    output = compiled(dot_source, filetype)

    return output

###############################################################################
###############################################################################
#### Configuration Schema                                                  ####
###############################################################################
###############################################################################

# Contains groups of attributes labeled by the strings in `allowed`
attribute_defaults = lambda key, allowed : {
        'description' : 'defaults for Graphviz {key}s'.format(key=key),
        'type' : 'dict',
        'default' : { key : defaults for key, _, defaults in allowed },
        'schema' : {
            key : {
                'description' : description,
                'type' : 'dict',
                'default' : defaults,
                'keyschema' : {
                    'description' : 'name',
                    },
                'valueschema' : {
                    'description' : 'value',
                    'type' : ['string', 'number', 'boolean'],
                    }
                } for key, description, defaults in allowed
            }
        }

CONFIG_SCHEMA = {
        'name' : {
            'description' : 'writer name',
            'regex' : 'dot',
            'default' : 'dot',
            },
        'filetype' : {
            'description' : 'output filetype',
            'allowed' : list(filetypes),
            'nullable' : True,
            },
        'file' : {
            'description' : 'output file name',
            'coerce' : 'optional_path',
            'nullable' : True,
            },
        'ranks' : {
            'description' : 'enable ranks',
            'type' : 'boolean',
            'default' : True,
            },
        'custom_edges' : {
            'description' : 'enable custom edges',
            'type' : 'boolean',
            'default' : True,
            },
        'custom_nodes' : {
            'description' : 'enable custom nodes',
            'type' : 'boolean',
            'default' : True,
            },
        'no_singletons' : {
            'description' : 'delete member nodes with neither parent nor child nodes',
            'type' : 'boolean',
            'default' : True,
            },
        'colors' : {
            'description' : 'add color to member nodes',
            'type' : 'boolean',
            'default' : True,
            },
        'unknowns' : {
            'description' : 'add parent nodes to members without any',
            'type' : 'boolean',
            'default' : True,
            },
        'warn_rank' : {
            'description' : 'if no_singletons=True, singletons with rank>=warn_rank trigger warnings when dropped',
            'coerce' : 'optional_rank_type',
            'default' : None,
            'nullable' : True,
            },
        'defaults' : {
                'description' : 'default Graphviz attributes',
                'type' : 'dict',
                'default' : {},
                'schema' : {
                    'graph' : attribute_defaults('graph', allowed=[
                        ('all', '', {})
                        ]),
                    'node' : attribute_defaults('node', allowed=[
                        ('all', 'all nodes', {}),
                        ('rank', 'rank nodes', {'color' : 'none'}),
                        ('unknown', 'nodes of unknown parents', {'style':'invis'}),
                        ('member', 'member nodes', {})
                        ]),
                    'edge' : attribute_defaults('edge', allowed=[
                        ('all', 'all edges', {'arrowhead':'none'}),
                        ('rank', 'edges between rank nodes', {'style':'invis'}),
                        ('unknown', 'edges coming from unknown parents', {}),
                        ]),
                    }
                },
        'family_colors' : {
                'description' : 'map of member keys to Graphviz colors',
                'type' : 'dict',
                'default' : {},
                'keyschema' : {
                    'description' : 'key',
                    'type' : 'string',
                    'required' : True,
                    },
                'valueschema' : {
                    'description' : 'color',
                    'type' : 'string',
                    'required' : True,
                    },
                },
        'nodes' : {
                'description' : 'custom Graphviz nodes',
                'type' : 'dict',
                'default' : {},
                'keyschema' : {
                    'type' : 'string',
                    },
                'valueschema' : {
                    'description' : 'a Graphviz node key',
                    'type' : 'dict',
                    'schema' : {
                        'rank' : {
                            'description' : 'the rank (i.e., year, semester, etc.) the node is in',
                            'coerce' : 'rank_type',
                            },
                        'attributes' : {
                            'description' : 'Graphviz node attributes',
                            'type' : 'dict',
                            'default' : {},
                            'keyschema' : {
                                'description' : 'name',
                                },
                            'valueschema' : {
                                'description' : 'value',
                                },
                            }
                        }
                    }
                },

        # Custom edges: Each entry in the list has a list of nodes, which are
        # used to represent a path from which to create edges (which is why
        # there must be at least two nodes in each list). There are also edge
        # attributes applied to all edges in the path.
        'edges' : {
            'description' : 'a list of custom Graphviz edges',
            'type' : 'list',
            'default' : [],
            'schema' : {
                'description' : 'edge',
                'type' : 'dict',
                'schema' : {
                    'nodes' : {
                        'description' : 'keys of nodes connected by this edge',
                        'type' : 'list',
                        'required' : True,
                        'minlength' : 2,
                        'schema' : {
                            'description' : 'key',
                            'type' : 'string',
                            }
                        },
                    'attributes' : {
                        'description' : 'Graphviz edge attributes',
                        'type' : 'dict',
                        'default' : {},
                        'keyschema' : {
                            'description' : 'name',
                            },
                        'valueschema' : {
                            'description' : 'value',
                            }
                        }
                    }
                },
            },

        }

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
                msg = 'custom {path_or_edge} {nodes} has undefined node: {key!r}'.format(path_or_edge=path_or_edge, nodes=nodes, key=key)
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

    # Find singletons
    keys = []
    warned = False
    for singleton in tree.singletons():

        key = singleton.key
        keys.append(key)

        # Warnings
        rank = singleton.is_ranked() and singleton.rank
        if warn_rank is not None and warn_rank <= rank:
            if not warned:
                logger = logging.getLogger(logger_name)
                msg = 'Member nodes with no parents, no children, and rank >= warn_rank == {warn_rank!r} were dropped:'.format(warn_rank=warn_rank)
                logger.warning(msg)
                warned = True
            msg = 'Dropped (key={key!r}, label={label!r}, rank={rank!r})'.format(key=key, label=singleton.label, rank=rank)
            logger.warning(msg)

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
            msg = 'family color map includes nonexistent member: {key!r}'.format(key=key)
            logging.getLogger(logger_name).warning(msg)
            continue
        family = tree[key]['family']
        if 'color' in family:
            msg = 'family of member {key!r} already assigned the color {color!r}'.format(key=key, color=color)
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
        key = '{key} Parent'.format(key=member.key)
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
    attributes for various types of items on the graph.
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

    subgraph = dot.Graph('dates{suffix}'.format(suffix=suffix), 'subgraph')
    node_defaults = dot.Defaults('node', node_defaults)
    edge_defaults = dot.Defaults('edge', edge_defaults)

    nodes, edges = [], []
    rank = min_rank
    while rank < max_rank:
        this_rank_key = '{rank}{suffix}'.format(rank=rank, suffix=suffix)
        next_rank_key = '{rank}{suffix}'.format(rank=rank+1, suffix=suffix)
        nodes.append(dot.Node(this_rank_key, attributes={'label' : rank}))
        edges.append(dot.Edge(this_rank_key, next_rank_key))
        rank += 1

    nodes.append(dot.Node('{rank}{suffix}'.format(rank=rank, suffix=suffix), attributes={'label' : rank}))

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
        ranks.append(dot.Rank(['{i}L'.format(i=i), '{i}R'.format(i=i)]))
        i += 1

    for key, node in tree.items():
        ranks[node['entity'].rank - min_rank].keys.append(key)

    return ranks

###############################################################################
###############################################################################
#### Writing Output                                                        ####
###############################################################################
###############################################################################

@logged
def compiled(src, filetype):
    '''
    If the filetype is DOT, return the raw DOT source code. Otherwise, use
    Graphviz to do the compiling.
    '''
    return compile_dot(src) if filetype == 'dot' else compile_fmt(src, filetype)

@logged
def compile_fmt(src, filetype):
    '''
    Uses Graphviz dot to convert the DOT source into the appropriate filetype.
    Returns the binary of that filetype.

    Note: Although Graphviz supports many formats, only a handful of them are
    permissible here. If you want to use those formats, pipe the DOT output of
    snutree into dot itself.
    '''

    # This should have been checked somewhere outside this function, but who knows?
    assert filetype in filetypes, 'filetype not properly cleaned'

    try:

        # `shell=True` is necessary for Windows, but not for Linux. The command
        # string is constant except for the validated {filetype}, so shell=True
        # should be fine
        result = subprocess.run('dot -T{filetype}'.format(filetype=filetype), check=True, shell=True,
                # The input will be a str and the output will be binary, but
                # subprocess.run requires they both be str or both be binary.
                # So, use binary and send the source in as binary (with default
                # encoding).
                input=bytes(src, sys.getdefaultencoding()),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE # Windows doesn't like it when stderr is left alone
                )
    except (OSError, subprocess.CalledProcessError) as exception:
        msg = 'had a problem compiling to {filetype}:\n{exception}\nCaptured Standard Error:\n{stderr}'.format(filetype=filetype, exception=exception, stderr=exception.stderr)
        raise SnutreeWriterError(msg)

    return result.stdout

@logged
def compile_dot(src):
    '''
    Converts the DOT source into bytes suitable for writing (bytes, not
    characters, are expected by the main output writer).
    '''
    return bytes(src, sys.getdefaultencoding())

