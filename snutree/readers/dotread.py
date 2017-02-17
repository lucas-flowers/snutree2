import re, pydotplus, logging
import networkx.drawing.nx_pydot as nx_pydot

def read_pydot(filename):
    with open(filename, 'r') as f:
        return pydotplus.parser.parse_dot_data(f.read())

def pydot_to_nx(pydot):
    '''
    Covert the pydot graph to an nx graph, populate it with members, and add
    pledge class semesters to those members.
    '''

    graph = nx_pydot.from_pydot(pydot)
    add_member_dicts(graph)
    add_pledge_classes(pydot, graph)
    remove_reciprocal_relationships(graph)
    return graph

def add_member_dicts(graph):

    # Add name and status from nodes
    for key in graph.nodes_iter():
        graph.node[key].update({'name' : key})

    # Add big brothers from edges
    for parent, child in graph.edges_iter():
        graph.node[child]['big_name'] = graph.node[parent]['name']

def add_pledge_classes(pydot, graph):
    '''
    Retrieve pledge classes from each pydot subgraph that has "rank=same", then
    set the pledge_semester field in each member's node attribute dictionary
    appropriately.
    '''

    semester_matcher = re.compile('((Fall|Spring) \d\d\d\d)')

    pledge_classes = {}
    for subgraph in pydot.get_subgraphs():

        # Only subgraphs with rank=same are actually pledge classes
        if subgraph.get_rank() == 'same':

            # Set of members in a pledge class
            pledge_class = set()

            for node in subgraph.get_nodes():

                # Pydot names include the quotes for some reason; remove them
                name = node.get_name().strip('"')

                match = semester_matcher.match(name)
                if match: # a semester

                    semester_name = match.group(1)

                    # If the semester is already mapped, add the current list
                    # of pledge class members to the list pledge_classes, and
                    # switch to using pledge_classes[semester_name] instead of
                    # pledge_class.
                    if semester_name in pledge_classes:
                        pledge_classes[semester_name] |= pledge_class
                        pledge_class = pledge_classes[semester_name]
                    # Otherwise, make a new mapping to pledge_class.
                    else:
                        pledge_classes[semester_name] = pledge_class

                else: # assumed to be a member
                    pledge_class.add(name)

    # Assign the field in member entries
    for semester, members in pledge_classes.items():
        for member in members:
            graph.node[member]['pledge_semester'] = semester

def remove_reciprocal_relationships(graph):
    '''
    Removes each big/little relationship that has a corresponding big/little
    relationship between the same members, but in the opposite direction. Print
    the relationships that were removed, so they can potentially be added to
    custom edges in settings.

    This is done because there should be no cycles in the tree, except for
    edges that required special handling.
    '''

    pairs = set()
    for parent, child in graph.edges_iter():
        if (child, parent) in graph.edges():
            pkey = graph.node[parent]['name']
            ckey = graph.node[child]['name']
            pairs.add(frozenset((pkey, ckey)))
            graph.node[parent]['big_name'] = None
            graph.node[child]['big_name'] = None

    if pairs:
        logging.warn('The following paths were removed, add to custom edges:')
        for pair in pairs:
            key1, key2 = tuple(pair)
            logging.warn([key1, key2, key1])

def get_rows(graph):

    return [node_dict for _, node_dict in graph.nodes_iter(data=True)]

def get_table(path):
    '''
    Read a DOT file into a pydotplus graph, convert that graph into an
    intermediate networkx graph (they're easier to deal with), and get a list
    of member entries from the networkx graph.
    '''

    pydot = read_pydot(path)
    graph = pydot_to_nx(pydot)
    return get_rows(graph)

