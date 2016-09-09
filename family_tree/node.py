from collections import defaultdict

def tree_from_records(records):
    '''
    Arguments
    =========

    records: Dict of records

    Returns
    =======

    A root node. Its descendents are nodes containing all the records in the
    argument `records`.

    '''

    # Dict of all nodes in the tree. Empty empty nodes are initialized with the
    # Node constructor (with default values for the its fields)
    nodes = defaultdict(Node)

    for key, record in records.items():

        # Add the record to the node corresponding to the record. If the node
        # has not been created yet, the defaultdict will create an empty one.
        node = nodes[key]
        node.record = record

        # Add the node as a child to the record's parent.
        #
        # Note: The defaultdict will create the root node implicitly, with the
        # key of None (since records without parents have parent_key values of
        # None).
        nodes[record.parent_key].children.append(node)

    return nodes[None]

class Node:

    def __init__(self, record=None, children=None):
        self.record = record
        self.children = [] if children is None else children

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

