
'''
Functions to declaratively create DOT objects.
'''

from . import model
from .model import ComponentType, GraphType

def create_graph_factory(graph_type):
    def GraphFactory(*args):
        if len(args) >= 1 and isinstance(args[0], str):
            identifier, statements = args[0], args[1:]
        else:
            identifier, statements = None, args
        return model.Graph(graph_type, identifier, statements)
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
        return model.Component(ComponentType.GRAPH, [], kwargs)
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
    return model.Graph(graph_type, identifier, statements)

def Node(*identifiers, **attributes):
    '''
    Construct a Node defaults or Node statement.
    '''
    if len(identifiers) <= 1:
        # Node(identifier, **attributes): Node
        # Node(**attributes): Node defaults
        return model.Component(ComponentType.NODE, identifiers, attributes)
    else:
        msg = f'Node() takes 0 or 1 identifiers but {len(identifiers)} were given'
        raise TypeError(msg)

def Edge(*identifiers, **attributes):
    '''
    Construct a Edge defaults or Edges statement.
    '''
    if len(identifiers) != 1:
        # Edge(*identifiers, **attributes): Edge(s)
        # Edge(**attributes): Edge defaults
        return model.Component(ComponentType.EDGE, identifiers, attributes)
    else:
        msg = f'Edge() takes 0 or >1 identifiers but {len(identifiers)} were given'
        raise TypeError(msg)

def Attribute(*args, **kwargs):
    '''
    Construct an attribute key-value pair.
    '''
    if len(kwargs) == 1 and not args:
        # Attribute(key=value)
        return model.Attribute(*kwargs.popitem())
    elif len(args) == 2 and not kwargs:
        # Attribute(key, value)
        return model.Attribute(*args)
    else:
        msg = f'Only Attribute(key, value) or Attribute(key=value) is permitted'
        raise TypeError(msg)

