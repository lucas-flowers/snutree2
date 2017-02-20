from abc import ABCMeta, abstractmethod
from collections import namedtuple

TABSTOP = 4

def indent(indent_level):
    return TABSTOP * indent_level * ' '

def dict_to_attr(attributes_dict, sep=','):
    '''
    Form a DOT attribute list from the provided dictionary, using the separator
    to separate attributes. The attributes will be sorted by key and value, to
    ensure consistency when compiling (i.e., to make the result code more
    diffable).
    '''

    dot_attributes = []
    for key, value in sorted(attributes_dict.items()):
        # If the value is a string bracketed by '<' and '>', use those instead
        bracketed = type(value) == str and len(value) > 1 and value[0::len(value)-1] == '<>'
        template = '{}="{}"' if not bracketed else '{}={}'
        dot_attributes.append(template.format(key, value))

    return sep.join(dot_attributes)

class DotCommon(metaclass=ABCMeta):

    def __init__(self, key, attributes=None):
        self.key = key
        self.attributes = attributes or {}

    @abstractmethod
    def to_dot(self, indent=0):
        pass

class Graph(DotCommon):

    graph_types = ('graph', 'digraph', 'subgraph')

    def __init__(self, key, graph_type, attributes=None, children=None):

        if graph_type not in Graph.graph_types:
            msg = 'Expected graph type in {}, but received: {}'
            vals = Graph.graph_types, graph_type
            raise ValueError(msg.format(*vals))

        self.graph_type = graph_type
        self.children = children or []
        super().__init__(key, attributes)

    def to_dot(self, indent_level=0):

        lines = []

        template = '{}{} "{}" {{'
        values = indent(indent_level), self.graph_type, self.key
        lines.append(template.format(*values))

        if self.attributes:
            sep = ';\n{}'.format(indent(indent_level+1))
            attributes = dict_to_attr(self.attributes, sep=sep)
            template = '{}{};'
            values = indent(indent_level+1), attributes
            lines.append(template.format(*values))

        for child in self.children:
            lines.append(child.to_dot(indent_level+1))

        template = '{}}}'
        value = indent(indent_level)
        lines.append(template.format(value))

        return '\n'.join(lines)

class Defaults(DotCommon):

    defaults_types = ('node', 'edge')

    def __init__(self, key, attributes=None):

        if key not in Defaults.defaults_types:
            msg = 'Expected defaults type in {}, but received: {}'
            vals = Defaults.defaults_types, key
            raise ValueError(msg.format(*vals))

        super().__init__(key, attributes)

    def to_dot(self, indent_level=0):
        attributes = dict_to_attr(self.attributes) or ''
        template = '{}{} [{}];'
        values = indent(indent_level), self.key, attributes
        return template.format(*values)

class Node(DotCommon):

    def to_dot(self, indent_level=0):

        template = ' [{}]'
        value = dict_to_attr(self.attributes)
        attributes = template.format(value) if value else ''

        template = '{}"{}"{};'
        values = indent(indent_level), self.key, attributes
        return template.format(*values)

class Edge(DotCommon):

    EdgeKey = namedtuple('EdgeKey', ['parent', 'child'])

    def __init__(self, parent_key, child_key, attributes=None):
        super().__init__(Edge.EdgeKey(parent_key, child_key), attributes)

    def to_dot(self, indent_level=0):

        template = ' [{}]'
        value = dict_to_attr(self.attributes)
        attributes = template.format(value) if value else ''

        template =  '{}"{}" -> "{}"{};'
        values = indent(indent_level), self.key.parent, self.key.child, attributes
        return template.format(*values)

class Rank:

    def __init__(self, keys=None):
        self.keys = keys or []

    def to_dot(self, indent_level=0):
        keys = ' '.join(['"{}"'.format(k) for k in sorted(self.keys, key=str)])
        template =  '{}{{rank=same {}}};'
        values = indent(indent_level), keys
        return template.format(*values)

