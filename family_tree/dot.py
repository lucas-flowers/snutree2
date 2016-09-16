from collections import namedtuple

def dict_to_dot_attributes(attributes_dict, sep=','):
    return sep.join(
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
            node_defaults=None, edge_defaults=None):

        if graph_type not in Graph.graph_types:
            raise ValueError(
                    'Expected graph type in {}, but received: {}'
                    .format(Graph.graph_types, graph_type)
                    )

        self.graph_type = graph_type
        self.children = children or []
        self.node_defaults = node_defaults or {}
        self.edge_defaults = edge_defaults or {}
        super().__init__(key, attributes)

    def to_dot(self):

        lines = []
        lines.append('{} "{}" {{'.format(self.graph_type, self.key))
        if self.attributes:
            lines.append('{};'.format(dict_to_dot_attributes(self.attributes, sep=';\n')))
        if self.node_defaults:
            lines.append('node [{}];'.format(dict_to_dot_attributes(self.node_defaults)))
        if self.edge_defaults:
            lines.append('edge [{}];'.format(dict_to_dot_attributes(self.edge_defaults)))
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

    def __init__(self, keys=None):
        self.keys = keys or []

    def to_dot(self):
        return '{{rank=same {}}};'.format(
                ' '.join(['"{}"'.format(key) for key in self.keys])
                )

