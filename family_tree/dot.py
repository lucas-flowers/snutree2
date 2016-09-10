from collections import namedtuple

def dict_to_dot_attributes(attributes_dict):
    return ','.join(
            ['{}="{}"'.format(key, value)
                for key, value in attributes_dict.items()]
            )

class DotCommon:

    def __init__(self, key, attributes=None):
        self.key = key
        self.attributes = attributes or {}

    def to_dot(self):
        raise NotImplementedError

class Graph(DotCommon):

    graph_types = ('graph', 'digraph', 'subgraph')

    def __init__(self, key, graph_type, children=None, attributes=None,
            default_node_attributes=None, default_edge_attributes=None):

        if graph_type not in Graph.graph_types:
            raise ValueError(
                    'Expected graph type in {}, but received: {}'
                    .format(Graph.graph_types, graph_type)
                    )

        self.graph_type = graph_type
        self.children = children or []
        self.default_node_attributes = default_node_attributes or {}
        self.default_edge_attributes = default_edge_attributes or {}
        super().__init__(key, attributes)

    def to_dot(self):

        lines = []
        lines.append('{} "{}" {{'.format(self.graph_type, self.key))
        lines.append(dict_to_dot_attributes(self.attributes) + ';' )
        if self.default_node_attributes:
            lines.append('node [{}];'.format(dict_to_dot_attributes(self.default_node_attributes)))
        if self.default_edge_attributes:
            lines.append('edge [{}];'.format(dict_to_dot_attributes(self.default_edge_attributes)))
        for child in self.children:
            lines.append(child.to_dot())
        lines.append('}')

        return '\n'.join(lines)

class Node(DotCommon):

    def to_dot(self):

        attr_string = dict_to_dot_attributes(self.attributes)

        if attr_string:
            return '"{}" [{}];'.format(self.key, attr_string)
        else:
            return '"{}";'.format(self.key)

class Edge(DotCommon):

    EdgeKey = namedtuple('EdgeKey', ['parent', 'child'])

    def __init__(self, parent_key, child_key, attributes=None):
        super().__init__(Edge.EdgeKey(parent_key, child_key), attributes)

    def to_dot(self):

        attr_string = dict_to_dot_attributes(self.attributes)

        if attr_string:
            return '"{}" -> "{}" [{}];'.format(self.key.parent, self.key.child, attr_string)
        else:
            return '"{}" -> "{}";'.format(self.key.parent, self.key.child)

class Rank:

    def __init__(self, keys):
        self.keys = keys or []

    def to_dot(self):
        return '{{rank=same {}}};'.format(
                ' '.join(['"{}"'.format(key) for key in self.keys])
                )

