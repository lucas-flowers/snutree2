'''
Utilities get members from a DOT file and turn it into a member list. Assumes
the DOT file is place nice and is friendly, as this is mainly for testing.
'''

import re
from io import StringIO
from contextlib import redirect_stdout
import networkx.drawing.nx_pydot as nx_pydot
from snutree.errors import SnutreeReaderError

CONFIG_SCHEMA = {} # No configuration

def get_table(f, **config):
    '''
    Read a DOT file into a pydotplus graph, convert that graph into an
    intermediate networkx graph (they're easier to deal with), and return a
    list of member dictionaries from the networkx graph.
    '''

    try:
        import pydotplus
    except ImportError: # 3.6: ModuleNotFoundError:
        msg = 'could not read DOT file: missing pydotplus package'
        raise SnutreeReaderError(msg)

    # Pydotplus catches all of its ParseExceptions at the end of parse_dot_data
    # and doesn't bother to rethrow them or store the messages in a log.
    # Instead, it prints the messages directly to stdout. So, we have to
    # capture stdout from parse_dot_data if there are any problems (indicated
    # by a return value of None).
    dot_code = f.read()
    captured_stderr = StringIO()
    with redirect_stdout(captured_stderr):
        pydot = pydotplus.parser.parse_dot_data(dot_code)

    if pydot is None:
        error_message = captured_stderr.getvalue()
        msg = 'could not read DOT file:\n{error_message}'.format(error_message=error_message)
        raise SnutreeReaderError(msg)
    else:
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
    Add names and bigs to the node attribute dictionaries in the graph, based
    on the values provided by pydot.
    '''

    for key in graph.nodes_iter():
        graph.node[key].update({'name' : key})

    for parent, child in graph.edges_iter():
        graph.node[child]['big_name'] = graph.node[parent]['name']

def add_pledge_classes(pydot, graph):
    '''
    Retrieve ranks from each pydot subgraph that has "rank=same", then set the
    semester field in each member's node attribute dictionary
    appropriately.
    '''

    semester_matcher = re.compile(r'((Fall|Spring) \d\d\d\d)')

    pledge_classes = {}
    subgraphs = (s for s in pydot.get_subgraphs() if s.get_rank() == 'same')
    for subgraph in subgraphs:

        # Get all the pledge class members
        pledge_class_members = set()
        for node in subgraph.get_nodes():

            # Pydot names include the quotes; remove them
            name = node.get_name().strip('"')

            semester_match = semester_matcher.match(name)
            if semester_match:

                semester_name = semester_match.group(1)

                # I don't want to bother with these cases
                if semester_name in pledge_classes:
                    msg = 'two pledge classes in the same semester: {semester_name}'.format(semester_name=semester_name)
                    raise ValueError(msg)

                pledge_classes[semester_name] = pledge_class_members

            else:

                # Assume it's a member
                pledge_class_members.add(name)

    # Assign the semester field
    for semester, members in pledge_classes.items():
        for member in members:
            graph.node[member]['semester'] = semester

