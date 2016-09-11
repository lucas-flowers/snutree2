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

    tree = nx.DiGraph()
    for key, record in records.items():
        for parent_key in record.parent_keys:
            tree.add_edge(
                    parent_key,
                    key,
                    **records[parent_key].dot_out_edge_attributes(records[key])
                    )

    # TODO combine this and the previous loop?
    for key, record in records.items():
        if key in tree:
            tree.add_node(key, **records[key].dot_attributes())

    return tree

def records_to_tree(records):

    graph = records_to_networkx(records)

    return graph


