import networkx as nx
from networkx.algorithms import dag
from collections import defaultdict
from family_tree.records import MemberRecord

def add_big_little_edges(graph):
    '''
    Add the big-little relationships (taken from the records in the nodes of
    the graph) as edges to the graph.
    '''

    for key, node_dict in graph.nodes(data=True):
        record = node_dict['record']
        if record.parent:
            graph.add_edge(node_dict['record'].parent, key)

def drop_orphans(graph):

    graph.remove_nodes_from([key for key, degree in graph.degree_iter() if degree == 0])


def add_node_attributes(graph, records):

    for key, record in records.items():
        if key in graph:
            graph.add_node(key, **records[key].dot_attributes())

    return graph

def add_families(graph, records):

    # Find strict roots
    root_keys = [key for key, in_degree in graph.in_degree().items() if in_degree == 0]

    # Find patriarchs and mark their families by their key
    #
    # This works under the assumption that any non-MemberRecord has only
    # MemberRecord children
    #
    # TODO old patriarchs mistakenly labeled
    for root_key in root_keys:
        if isinstance(records[root_key], MemberRecord):
            graph.node[root_key]['family'] = root_key
            for descendant_key in dag.descendants(graph, root_key):
                graph.node[descendant_key]['family'] = root_key
        else:
            root_keys += graph.successors(root_key)

    print(graph.node['1031']['family'])

def decorate_tree(graph):

    add_big_little_edges(graph)
    drop_orphans(graph)
    # add_node_attributes(graph, records)
    # add_families(graph, records)

    return graph


