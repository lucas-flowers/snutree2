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
            tree.add_edge(parent_key, key)

    return tree

def decorate_tree(tree, records):

    for key in tree:
        tree.node[key]['label'] = records[key].label()


def records_to_tree(records):

    graph = records_to_networkx(records)
    decorate_tree(graph, records)

    return graph


