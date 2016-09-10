from collections import namedtuple

class DotCommon:

    def __init__(self, key, attributes=None):
        self.key = key
        self.attributes = attributes or {}

    def attributes_to_dot(self):
        return ','.join(
                ['{}="{}"'.format(key, value)
                    for key, value in self.attributes.items()]
                )

    def to_dot(self):
        raise NotImplementedError

class Graph(DotCommon):

    graph_types = ('graph', 'digraph', 'subgraph')

    def __init__(self, key, graph_type, children=None, attributes=None):

        if graph_type not in Graph.graph_types:
            raise ValueError(
                    'Expected graph type in {}, but received: {}'
                    .format(Graph.graph_types, graph_type)
                    )

        self.graph_type = graph_type
        self.children = children or {}
        super().__init__(key, attributes)

    def to_dot(self):

        lines = []
        lines.append('{} "{}" {{'.format(self.graph_type, self.key))
        lines.append(self.attributes_to_dot() + ';' )
        for child in self.children:
            lines.append(child.to_dot())
        lines.append('}')

        return '\n'.join(lines)

class Node(DotCommon):

    def to_dot(self):

        attr_string = self.attributes_to_dot()

        if attr_string:
            return '"{}" [{}];'.format(self.key, attr_string)
        else:
            return '"{}";'.format(self.key)

class Edge(DotCommon):

    EdgeKey = namedtuple('EdgeKey', ['parent', 'child'])

    def __init__(self, parent_key, child_key, attributes=None):
        super().__init__(Edge.EdgeKey(parent_key, child_key), attributes)

    def to_dot(self):

        attr_string = self.attributes_to_dot()

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

