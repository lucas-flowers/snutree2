#!/usr/bin/python3
import jsonschema as jsch

# Represents a Graphviz list of attributes
attributes = {
        'type' : 'object',
        'additionalProperties' : {
            'type' : ['string', 'number', 'boolean'],
            }
        }

# For graphs, nodes, and edges, default attributes are set for each category of
# node used in the family tree program.
def defaults(*categories):
    return {
            'type' : 'object',
            'properties' : {
                category : attributes for category in categories
                },
            'additionalProperties' : False
            }
graph_defaults = defaults('all')
node_defaults = defaults('all', 'semester', 'unknown', 'member')
edge_defaults = defaults('all', 'semester', 'unknown')

# Map of families (labeled by their patriarchs) to family colors
color_mapping = {
        'type' : 'object',
        'additionalProperties' : {
            'type' : 'string'
            }
        }

# A semester (used for placing the node), and optional attributes for the node
# located at that semester.
node = {
        'type' : 'object',
        'properties' : {
            'semester' : {
                'type' : 'string',
                },
            'attributes' : attributes,
            },
        'additionalProperties': False,
        'required' : ['semester'],
        }


nodes = {
        'type' : 'object',
        'additionalProperties' : node,
        }

# A list of nodes forming a path. At least two nodes are required to make a path.
node_path = {
        'type' : 'array',
        'items' : {
            'type' : 'string',
            'minItems' : 2,
            }
        }

# A list of nodes, plus optional attributes for the edges connecting them
edges = {
        'type' : 'array',
        'items' : {
            'type' : 'object',
            'properties' : {
                'nodes' : node_path,
                'attributes' : attributes,
                },
            'additionalProperties' : False,
            'required' : ['nodes'],
            }
        }

seed = {
        'type' : 'integer',
        }

schema = {
        'type' : 'object',
        'properties' : {
            'nodes' : nodes,
            'edges' : edges,
            'seed' : seed,
            'family_colors' : color_mapping,
            'edge_defaults' : edge_defaults,
            'node_defaults' : node_defaults,
            'graph_defaults' : graph_defaults,
            },
        'additionalProperties' : False,
        }

def validate(settings):
    try:
        jsch.validate(settings, schema)
    except jsch.exceptions.ValidationError as e:
        raise SettingsException('Error in settings file, in "{}": {}'.format(
            '" -> "'.join(e.path),
            e.message)
            )

class SettingsException(Exception):
    pass


