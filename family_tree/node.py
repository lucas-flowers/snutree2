
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

    # TODO use defaultdict for `nodes`
    roots = [] # List of root nodes of the tree
    nodes = {} # Dict of all nodes in the tree
    for key, record in records.items():

        # A record already found has this node as its parent
        if key in nodes:
            node = nodes[key]
            node.record = record

        # No record already found has made this node its parent
        else:
            node = Node(records[key])
            nodes[key] = node

        # This node has a parent, and the parent has already been found
        if record.parent_key in nodes:
            nodes[record.parent_key].children.append(node)
        # This node has a parent, but the parent has not been found yet
        elif record.parent_key:
            nodes[record.parent_key] = Node(children=[node])
        # This node has no parent; it is a root node
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

