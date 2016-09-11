import networkx as nx
from networkx.algorithms import dag
from collections import defaultdict
from family_tree.records import MemberRecord

def records_to_networkx(records):
    '''
    Arguments
    =========

    records: Dict of records

    Returns
    =======

    A networkx DiGraph representing the family tree. Each node in the DiGraph
    is a key for some corresponding record.

    Note
    ====

    A basic tree structure is not enough, because the existence of
    Reorganization records allows for the potential that some nodes might have
    more than one parent.

    '''

def add_edges(graph, records):

    for key, record in records.items():
        child_record = records[key]
        for parent_key in record.parent_keys:
            parent_record = records[parent_key]
            graph.add_edge(parent_key, key,
                    **parent_record.dot_out_edge_attributes(child_record))

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

def records_to_tree(records):

    graph = nx.DiGraph()
    add_edges(graph, records)
    add_node_attributes(graph, records)
    add_families(graph, records)

    return graph


