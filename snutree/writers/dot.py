import logging
from snutree import dot
from snutree.logging import logged
from snutree.colors import ColorPicker
from snutree.tree import TreeErrorCode, TreeError # TODO make writer errors

# @option('family_colors')
@logged
def add_colors(tree):
    '''
    Add colors to member nodes, based on their family. Uses settings
    dictionary to provide initial colors, and generates the rest as needed.
    '''

    family_colors = tree.settings['family_colors']
    color_picker = ColorPicker.from_graphviz()

    for key, color in family_colors.items():

        if key not in tree.graph.node:
            msg = f'family color map includes nonexistent member: {key!r}'
            logging.getLogger(__name__).warning(msg)

        else:

            family = tree.graph.node[key]['family']
            if 'color' in family:
                code = TreeErrorCode.FAMILY_COLOR_CONFLICT
                msg = f'family of member {key!r} already assigned the color {color!r}'
                raise TreeError(code, msg)

            color_picker.use(color)
            tree.graph.node[key]['family']['color'] = color

    # The nodes are sorted first, to ensure that the same colors are used
    # for the same input data.
    for key, node_dict in sorted(tree.graph.nodes_iter(data=True)):
        family_dict = node_dict.get('family')
        if family_dict is not None:
            if 'color' not in family_dict:
                family_dict['color'] = next(color_picker)

            node_dict['attributes']['dot']['color'] = family_dict['color']

@logged
def to_dot_graph(tree):
    '''
    Convert the tree into an object representing a DOT file, then return
    that object.
    '''

    # TODO move
    if tree.settings['layout']['family_colors']:
        add_colors(tree)

    members = create_tree_subgraph(tree, 'members')

    graph_defaults = tree.settings['graph_defaults']['all']
    dotgraph = dot.Graph('family_tree', 'digraph', attributes=graph_defaults)

    node_defaults = dot.Defaults('node', tree.settings['node_defaults']['all'])
    edge_defaults = dot.Defaults('edge', tree.settings['edge_defaults']['all'])

    if tree.settings['layout']['ranks']:
        min_rank, max_rank = tree.get_rank_bounds()
        max_rank += 1 # always include one extra, blank rank at the end
        dates_left = create_date_subgraph(tree, 'L', min_rank, max_rank)
        dates_right = create_date_subgraph(tree, 'R', min_rank, max_rank)
        ranks = create_ranks(tree, min_rank, max_rank)
        dotgraph.children = [node_defaults, edge_defaults, dates_left, members, dates_right] + ranks

    else:
        dotgraph.children = [node_defaults, edge_defaults, members]

    return dotgraph

def create_date_subgraph(tree, suffix, min_rank, max_rank):
    '''
    Return a DOT subgraph containing the labels for each rank. The `suffix`
    is appended to the end of the keys of the subgraph's labels, so more
    than one subgraph can be made, using different suffixes.
    '''

    subgraph = dot.Graph(f'dates{suffix}', 'subgraph')

    node_defaults = dot.Defaults('node', tree.settings['node_defaults']['rank'])
    edge_defaults = dot.Defaults('edge', tree.settings['edge_defaults']['rank'])

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

def create_tree_subgraph(tree, subgraph_key):
    '''
    Create and return the DOT subgraph that will contain the member nodes
    and their relationships.
    '''

    dotgraph = dot.Graph(subgraph_key, 'subgraph')

    node_defaults = dot.Defaults('node', tree.settings['node_defaults']['member'])

    nodes = []
    for key, node_dict in tree.ordered_nodes():
        nodes.append(dot.Node(key, node_dict['attributes']['dot'])) # TODO validate later

    edges = []
    for parent_key, child_key, edge_dict in tree.ordered_edges():
        edges.append(dot.Edge(parent_key, child_key, edge_dict['attributes']['dot'])) # TODO validate later

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

    for key, entity in tree.nodes_iter('entity'):
        ranks[entity.rank - min_rank].keys.append(key)

    return ranks

