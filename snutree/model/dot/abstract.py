
'''
Underlying representations of DOT objects.
'''

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

class StringEnum(Enum):
    def __str__(self):
        return self.value

class ComponentType(StringEnum):
    NODE = 'node'
    EDGE = 'edge'
    GRAPH = 'graph'

class EdgeOp(StringEnum):
    DIRECTED = ' -> '
    UNDIRECTED = ' -- '

class GraphType(StringEnum):
    GRAPH = 'graph'
    DIGRAPH = 'digraph'
    SUBGRAPH = 'subgraph'
    STRICT_DIGRAPH = 'strict digraph'
    STRICT_GRAPH = 'strict graph'

@dataclass
class Attribute:

    key: str
    value: object

    def to_blocks(self):
        return [str(self) + ';']

    def __str__(self):
        return (
            f'{self.key}="{self.value}"'
            if isinstance(self.value, str) and not re.match(r'^<.+>$', self.value) else
            f'{self.key}={self.value}'
        )

@dataclass
class Component:

    component_type: ComponentType
    identifiers: List[str]
    _attributes: Dict[str, object]

    EDGE_OP = EdgeOp.DIRECTED

    @property
    def attributes(self):
        return [
            Attribute(key, value)
            for key, value in self._attributes.items()
        ]

    def to_blocks(self):
        return [str(self) + ';']

    def __str__(self):

        if self.identifiers:
            is_attribute_statement = False
            identifiers = self.identifiers
        else:
            is_attribute_statement = True
            identifiers = [self.component_type]

        identifier_string = str(self.EDGE_OP).join(
            f'{identifier}' if isinstance(identifier, ComponentType) else f'"{identifier}"'
            for identifier in identifiers
        )

        attribute_string = ','.join(map(str, self.attributes))

        return (
            f'{identifier_string} [{attribute_string}]'
            if attribute_string or is_attribute_statement else
            identifier_string
        )

@dataclass
class Graph:

    graph_type: GraphType
    identifier: str
    statements: List[object]

    TAB_STOP = 4
    TAB_CHAR = ' '

    def to_blocks(self):

        if not self.graph_type and not self.identifier:
            begin = f'{{'
        elif not self.identifier:
            begin = f'{self.graph_type} {{'
        else:
            begin = f'{self.graph_type} "{self.identifier}" {{'

        statements = [
            substatement
            for statement in self.statements if statement
            for substatement in statement.to_blocks()
        ]

        end = f'}}'

        return [begin, statements, end]

    @classmethod
    def to_lines(cls, nested, level=0):
        indent = level * cls.TAB_STOP * cls.TAB_CHAR
        for item in nested:
            if isinstance(item, list):
                yield from cls.to_lines(item, level=level+1)
            else:
                yield f'{indent}{item}\n'

    def __str__(self):
        return ''.join(self.to_lines(self.to_blocks()))

