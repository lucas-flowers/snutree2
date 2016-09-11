import networkx as nx
from collections import defaultdict

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

def records_to_tree(records):

    graph = nx.DiGraph()
    add_edges(graph, records)
    add_node_attributes(graph, records)

    return graph


