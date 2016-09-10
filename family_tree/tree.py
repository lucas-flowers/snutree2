import networkx as nx
from collections import defaultdict

def tree_from_records(records):
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
            tree.add_edge(parent_key, key)

    return tree

