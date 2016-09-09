from collections import defaultdict

def tree_from_records(records):
    '''
    Arguments
    =========

    records: Dict of records

    Returns
    =======


    Set of root nodes, whose descendents are nodes containing all the records
    in the argument.

    '''

    # List of root nodes of the tree
    roots = []

    # Dict of all nodes in the tree. Empty empty nodes are initialized with the
    # Node constructor (with default values for the its fields)
    nodes = defaultdict(Node)

    for key, record in records.items():

        # The node corresponding to this record. If the node has not been
        # created yet, the defaultdict will create an empty one.
        node = nodes[key]
        node.record = record

        # If there is a parent key, add the node as a child to the record's
        # parent (create the parent node if it doesn't exist)
        if record.parent_key:
            nodes[record.parent_key].children.append(node)

        # If there is no parent key, then this is a root node
        else:
            roots.append(node)

    return Node(None, roots)

class Node:

    def __init__(self, record=None, children=None):
        self.record = record
        self.children = [] if children is None else children

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

