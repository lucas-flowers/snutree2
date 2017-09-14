'''
Tools used to print the tree to DOT code.
'''

from abc import ABCMeta
from collections import namedtuple
from snutree.utilities.indent import Indent

class DotCommon(metaclass=ABCMeta):

    def __init__(self, key, attributes=None):
        self.key = key
        self.attributes = attributes.copy() if attributes else {}

    def to_dot(self, indent=None):
        indent = indent or Indent()
        self_dot = str(self)
        return '{indent}{self_dot}'.format(indent=indent, self_dot=self_dot) if self_dot else ''

    def attributes_to_dot(self, sep=','):
        '''
        Form a DOT attribute list from the object's attribute dictionary, using
        the separator to separate attributes. The attributes will be sorted by
        key and value, to ensure consistency when compiling (i.e., to make the
        result code more diffable).
        '''

        attributes = []
        for key, value in sorted(self.attributes.items()):
            # If the value is a string bracketed by '<' and '>', use those instead
            bracketed = isinstance(value, str) and len(value) > 1 and value[0::len(value)-1] == '<>'
            kv_pair = '{key}="{value}"'.format(key=key, value=value) if not bracketed else '{key}={value}'.format(key=key, value=value)
            attributes.append(kv_pair)

        return sep.join(attributes)

class Graph(DotCommon):

    graph_types = ('graph', 'digraph', 'subgraph')

    def __init__(self, key, graph_type, attributes=None, children=None):

        if graph_type not in Graph.graph_types:
            msg = 'Expected graph type in {graph_types}, but received: {graph_type}'.format(graph_types=Graph.graph_types, graph_type=graph_type)
            raise ValueError(msg)

        self.graph_type = graph_type
        self.children = children or []
        super().__init__(key, attributes)

    def to_dot(self, indent=None):

        lines = []
        indent = indent or Indent()

        lines.append('{indent}{graph_type} "{key}" {{'.format(indent=indent, graph_type=self.graph_type, key=self.key))
        with indent.indented():
            if self.attributes:
                attributes = self.attributes_to_dot(sep=';\n{indent}'.format(indent=indent))
                lines.append('{indent}{attributes};'.format(indent=indent, attributes=attributes))
            for child in self.children:
                line = child.to_dot(indent)
                if line: # some children might represent empty strings
                    lines.append(line)
        lines.append('{indent}}}'.format(indent=indent))

        return '\n'.join(lines)

class Defaults(DotCommon):

    defaults_types = ('node', 'edge')

    def __init__(self, key, attributes=None):
        if key not in Defaults.defaults_types:
            msg = 'Expected defaults type in {defaults_types}, but received: {key}'.format(defaults_types=Defaults.defaults_types, key=key)
            raise ValueError(msg)
        super().__init__(key, attributes)

    def __str__(self):
        kv_pairs = self.attributes_to_dot()
        return '{key} [{kv_pairs}];'.format(key=self.key, kv_pairs=kv_pairs) if kv_pairs else ''

class Node(DotCommon):

    def __str__(self):
        kv_pairs = self.attributes_to_dot()
        attributes = ' [{kv_pairs}]'.format(kv_pairs=kv_pairs) if kv_pairs else ''
        return '"{key}"{attributes};'.format(key=self.key, attributes=attributes)

class Edge(DotCommon):

    EdgeKey = namedtuple('EdgeKey', ['parent', 'child'])

    def __init__(self, parent_key, child_key, attributes=None):
        super().__init__(Edge.EdgeKey(parent_key, child_key), attributes)

    def __str__(self):
        kv_pairs = self.attributes_to_dot()
        attributes = ' [{kv_pairs}]'.format(kv_pairs=kv_pairs) if kv_pairs else ''
        return '"{pkey}" -> "{ckey}"{attributes};'.format(pkey=self.key.parent, ckey=self.key.child, attributes=attributes)

class Rank(DotCommon):

    def __init__(self, keys=None):
        self.keys = keys or []

    def __str__(self):
        keys = ' '.join(['"{key}"'.format(key=key) for key in sorted(self.keys, key=str)])
        return '{{rank=same {keys}}};'.format(keys=keys)

