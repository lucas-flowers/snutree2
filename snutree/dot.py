from abc import ABCMeta, abstractmethod
from collections import namedtuple
from .utilities import Indent

'''
Tools used to print the tree to DOT code.
'''

class DotCommon(metaclass=ABCMeta):

    def __init__(self, key, attributes=None):
        self.key = key
        self.attributes = attributes or {}

    def to_dot(self, indent=None):
        indent = indent or Indent()
        return f'{indent}{self}'

    def attributes_to_dot(self, sep=','):
        '''
        Form a DOT attribute list from the object's attribute dictionary, using
        the separator to separate attributes. The attributes will be sorted by
        key and value, to ensure consistency when compiling (i.e., to make the
        result code more diffable).
        '''

        dot_attributes = []
        for key, value in sorted(self.attributes.items()):
            # If the value is a string bracketed by '<' and '>', use those instead
            bracketed = isinstance(value, str) and len(value) > 1 and value[0::len(value)-1] == '<>'
            kv_pair = f'{key}="{value}"' if not bracketed else f'{key}={value}'
            dot_attributes.append(kv_pair)

        return sep.join(dot_attributes)

class Graph(DotCommon):

    graph_types = ('graph', 'digraph', 'subgraph')

    def __init__(self, key, graph_type, attributes=None, children=None):

        if graph_type not in Graph.graph_types:
            msg = f'Expected graph type in {Graph.graph_types}, but received: {graph_type}'
            raise ValueError(msg)

        self.graph_type = graph_type
        self.children = children or []
        super().__init__(key, attributes)

    def to_dot(self, indent=None):

        lines = []
        indent = indent or Indent()

        lines.append(f'{indent}{self.graph_type} "{self.key}" {{')
        with indent.indented():
            if self.attributes:
                attributes = self.attributes_to_dot(sep=f';\n{indent}')
                lines.append(f'{indent}{attributes};')
            for child in self.children:
                lines.append(child.to_dot(indent))
        lines.append(f'{indent}}}')

        return '\n'.join(lines)

class Defaults(DotCommon):

    defaults_types = ('node', 'edge')

    def __init__(self, key, attributes=None):
        if key not in Defaults.defaults_types:
            msg = f'Expected defaults type in {Defaults.defaults_types}, but received: {key}'
            raise ValueError(msg)
        super().__init__(key, attributes)

    def __str__(self):
        # TODO remove empty brackets
        attributes = self.attributes_to_dot() or ''
        return f'{self.key} [{attributes}];'

class Node(DotCommon):

    def __str__(self):
        kv_pairs = self.attributes_to_dot()
        attributes = f' [{kv_pairs}]' if kv_pairs else ''
        return f'"{self.key}"{attributes};'

class Edge(DotCommon):

    EdgeKey = namedtuple('EdgeKey', ['parent', 'child'])

    def __init__(self, parent_key, child_key, attributes=None):
        super().__init__(Edge.EdgeKey(parent_key, child_key), attributes)

    def __str__(self):
        kv_pairs = self.attributes_to_dot()
        attributes = f' [{kv_pairs}]' if kv_pairs else ''
        return f'"{self.key.parent}" -> "{self.key.child}"{attributes};'

class Rank(DotCommon):

    def __init__(self, keys=None):
        self.keys = keys or []

    def __str__(self):
        keys = ' '.join([f'"{key}"' for key in sorted(self.keys, key=str)])
        return f'{{rank=same {keys}}};';

