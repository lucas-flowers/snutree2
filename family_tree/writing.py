from collections import defaultdict
from family_tree import dot
from family_tree.semester import semester_range

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

default_semester_edge = {
        'style' : 'invis',
        }

default_semester_node = {
        'color' : 'none',
        'fontsize' : 20,
        'fontname' : 'georgia',
        }

def semester_bounds(graph, records):
    # Note: Change this if it is too slow
    return min([records[key].semester for key in graph]), \
            max([records[key].semester for key in graph])

def create_date_subgraph(key, min_semester, max_semester):

    subgraph = dot.Graph(
            'dates{}'.format(key),
            'subgraph',
            default_node_attributes=default_semester_node,
            default_edge_attributes=default_semester_edge,
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

def create_tree_subgraph(key, graph, records):

    dotgraph = dot.Graph(key, 'subgraph', default_node_attributes=member_node_defaults)

    # TODO add nodes
    nodes = []

    edges = []
    for parent_key, child_key in graph.edges(): # TODO also unpack with data=
        edges.append(dot.Edge(parent_key, child_key))

    dotgraph.children = nodes + edges

    return dotgraph

def create_ranks(graph, records):

    ranks = {}
    for key in graph.nodes():
        semester = records[key].semester
        if semester in ranks:
            ranks[semester].keys.append(key)
        else:
            ranks[semester] = dot.Rank([
                    '{}L'.format(semester),
                    '{}R'.format(semester),
                    key,
                    ])

    return list(ranks.values())



def create_graph(graph, records):

    min_semester, max_semester = semester_bounds(graph, records)
    dates_left = create_date_subgraph('L', min_semester, max_semester)
    dates_right = create_date_subgraph('R', min_semester, max_semester)
    tree = create_tree_subgraph('members', graph, records)
    ranks = create_ranks(graph, records)

    dotgraph = dot.Graph(
            'family_tree',
            'digraph',
            attributes=graph_defaults,
            default_node_attributes=node_defaults,
            default_edge_attributes=edge_defaults,
            )
    dotgraph.children = [dates_left, tree, dates_right] + ranks

    return dotgraph

