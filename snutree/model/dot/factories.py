
'''
Functions to declaratively create DOT objects.
'''

from . import abstract
from .abstract import ComponentType, GraphType

def create_graph_factory(graph_type):
    def GraphFactory(*args):
        if len(args) >= 1 and isinstance(args[0], str):
            identifier, statements = args[0], args[1:]
        else:
            identifier, statements = None, args
        return abstract.Graph(graph_type, identifier, statements)
    return GraphFactory

StrictGraph = create_graph_factory(GraphType.STRICT_GRAPH)
StrictDigraph = create_graph_factory(GraphType.STRICT_DIGRAPH)
Digraph = create_graph_factory(GraphType.DIGRAPH)

def Graph(*args, **kwargs):
    '''
    Construct a Graph defaults statement or a Graph.
    '''
    if not args and not kwargs:
        # Graph(): Empty nameless graph
        return create_graph_factory(GraphType.GRAPH)()
    elif not args and kwargs:
        # Graph(**attributes): Default graph with attributes
        return abstract.Component(ComponentType.GRAPH, [], kwargs)
    elif args and not kwargs:
        # Graph(*statements): Nameless graph
        # Graph(identifier): Empty named graph
        # Graph(identifier, *statements):  Named graph
        return create_graph_factory(GraphType.GRAPH)(*args)
    else: # args and kwargs
        msg = f'Only Graph(), Graph(*identifier_or_statements), or Graph(**attributes) are permitted'
        raise TypeError(msg)

def Subgraph(*args):
    '''
    Construct a Subgraph.
    '''
    if len(args) >= 1 and isinstance(args[0], str):
        graph_type, identifier, statements = GraphType.SUBGRAPH, args[0], args[1:]
    else:
        graph_type, identifier, statements = None, None, args
    return abstract.Graph(graph_type, identifier, statements)

def Node(*identifiers, **attributes):
    '''
    Construct a Node defaults or Node statement.
    '''
    if not identifiers and not attributes:
        msg = f'Node defaults must contain attributes'
        raise TypeError(msg)
    elif not identifiers and attributes:
        # Node(**attributes): Default node with attributes
        return abstract.Component(ComponentType.NODE, identifiers, attributes)
    elif len(identifiers) == 1:
        # Node(identifier, **attributes): Node with or without attributes
        return abstract.Component(ComponentType.NODE, identifiers, attributes)
    else: # len(identifiers) > 1
        msg = f'Node() takes 0 or 1 identifiers but {len(identifiers)} were given'
        raise TypeError(msg)

def Edge(*identifiers, **attributes):
    '''
    Construct a Edge defaults or Edges statement.
    '''
    if not identifiers and not attributes:
        msg = f'Edge defaults must contain attributes'
        raise TypeError(msg)
    elif not identifiers and attributes:
        # Edge(**attributes): Default edge with attributes
        return abstract.Component(ComponentType.EDGE, identifiers, attributes)
    elif len(identifiers) == 1:
        msg = f'Edge() takes 0 or >1 identifiers but {len(identifiers)} were given'
        raise TypeError(msg)
    else: # len(identifiers) > 1
        # Edge(*identifiers, **attributes): Edges with or without attributes
        return abstract.Component(ComponentType.EDGE, identifiers, attributes)

def Attribute(*args, **kwargs):
    '''
    Construct an attribute key-value pair.
    '''
    if len(kwargs) == 1 and not args:
        # Attribute(key=value)
        return abstract.Attribute(*kwargs.popitem())
    elif len(args) == 2 and not kwargs:
        # Attribute(key, value)
        return abstract.Attribute(*args)
    else:
        msg = f'Only Attribute(key, value) or Attribute(key=value) is permitted'
        raise TypeError(msg)

