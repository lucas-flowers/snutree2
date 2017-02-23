import re, pydotplus
import networkx.drawing.nx_pydot as nx_pydot

'''
Utilities get members from a DOT file and turn it into a member list. Assumes
the DOT file is place nice and is friendly. Mainly intended for testing.
'''


def get_members(f):
    '''
    Read a DOT file into a pydotplus graph, convert that graph into an
    intermediate networkx graph (they're easier to deal with), and return a
    list of member entries from the networkx graph.
    '''

    pydot = pydotplus.parser.parse_dot_data(f.read())
    graph = pydot_to_nx(pydot)
    return [node_dict for _, node_dict in graph.nodes_iter(data=True)]

def pydot_to_nx(pydot):
    '''
    Convert the pydot graph to an nx graph, populate it with members, add
    pledge class semesters to those members, and return the nx graph.
    '''

    graph = nx_pydot.from_pydot(pydot)
    add_member_dicts(graph)
    add_pledge_classes(pydot, graph)
    return graph

def add_member_dicts(graph):
    '''
    Add names and big brothers to the node attribute dictionaries in the graph,
    based on the values provided by pydot.
    '''

    for key in graph.nodes_iter():
        graph.node[key].update({'name' : key})

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
    subgraphs = (s for s in pydot.get_subgraphs() if s.get_rank() == 'same')
    for subgraph in subgraphs:

        # Get all the pledge class members
        pledge_class_members = set()
        for node in subgraph.get_nodes():

            # Pydot names include the quotes for some reason; remove them
            name = node.get_name().strip('"')

            semester_match = semester_matcher.match(name)
            if semester_match:

                semester_name = semester_match.group(1)

                # I don't want to bother with these case
                if semester_name in pledge_classes:
                    msg = 'two pledge classes in the same semester: {}'
                    raise ValueError(msg.format(semester_name))

                pledge_classes[semester_name] = pledge_class_members

            else:

                # Assume it's a member
                pledge_class_members.add(name)

    # Assign the pledge_semester field
    for semester, members in pledge_classes.items():
        for member in members:
            graph.node[member]['pledge_semester'] = semester

