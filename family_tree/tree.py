import networkx as nx
from networkx.algorithms import dag
from collections import defaultdict
from family_tree.records import MemberRecord

def drop_orphans(graph):

    graph.remove_nodes_from([key for key, degree in graph.degree_iter() if degree == 0])


def add_node_attributes(graph):

    for key, node_dict in graph.nodes_iter(data=True):
        record = node_dict['record']
        node_dict['dot_node_attributes'] = record.dot_node_attributes()

def add_edge_attributes(graph):

    for parent_key, child_key, edge_dict in graph.edges_iter(data=True):
        parent_record = graph.node[parent_key]['record']
        child_record = graph.node[child_key]['record']
        edge_dict['dot_edge_attributes'] = \
                parent_record.dot_edge_attributes(child_record)

def add_families(graph):

    # Members-only graph
    members_only = graph.subgraph(
            [key for key, node_dict in graph.nodes_iter(data=True)
                if isinstance(node_dict['record'], MemberRecord)]
            )

    # Find heads of members-only graph
    family_heads = [key for key, in_degree in members_only.in_degree().items()
            if in_degree == 0]

    # Mark descendants of the heads
    for head_key in family_heads:
        graph.node[head_key]['record'].family = head_key
        for descendant_key in dag.descendants(members_only, head_key):
            graph.node[descendant_key]['record'].family = head_key

def decorate_tree(graph):

    drop_orphans(graph)
    add_node_attributes(graph)
    add_edge_attributes(graph)
    add_families(graph)

    return graph


