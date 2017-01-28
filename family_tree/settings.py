import yaml
from cerberus import Validator
from family_tree.semester import Semester

def retrieve_settings(path):

    with open(path, 'r') as f:
        settings = yaml.load(f)

    settings = settings_schema.validated(settings)
    if settings:
        return settings
    else:
        raise Exception(str(settings_schema.errors))

sources = frozenset({'csv', 'mysql', 'dot'})

flags = [
        'semesters',
        'custom_edges',
        'custom_nodes',
        'no_singletons',
        'family_colors',
        'unknowns',
        ]

# A required string; must be nonempty and not None
nonempty_string = {
        'type' : 'string',
        'required' : True,
        'empty' : False,
        'nullable' : False,
        }

# An optional string defaulting to None; must be nonempty if it does exist
optional_nonempty_string = {
        'type' : 'string',
        'default' : None,
        'empty' : False,
        'nullable' : True,
        }

# Optional boolean with True default
optional_boolean = {
        'type' : 'boolean',
        'default' : True,
        }

# Graphviz attributes
attributes = {
        'type' : 'dict',
        'default' : {},
        'valueschema' : {
            'type' : ['string', 'number', 'boolean']
            }
        }

# Contains groups of attributes labeled by the strings in `allowed`
dot_defaults = lambda *allowed : {
        'type' : 'dict',
        'nullable' : False,
        'default' : { a : {} for a in allowed },
        'keyschema' : {
            'allowed' : allowed,
            },
        'valueschema' : attributes
        }

# Schema for overall YAML settings dict
settings_schema = Validator({

    # Output file information
    'output' : {
        'type' : 'dict',
        'required' : True,
        'schema' : {
            'folder' : nonempty_string,
            'name' : nonempty_string,
            },
        },

    # Input can be exactly one of: A DOT file, a CSV file, or the database.
    'dot' : {
        'type' : 'dict',
        'excludes' : list(sources - {'dot'}),
        'required' : True,
        'schema' : {
            'members' : nonempty_string
            }
        },
    'csv' : {
        'type' : 'dict',
        'excludes' : list(sources - {'csv'}),
        'required' : True,
        'schema' : {
            'members' : nonempty_string,
            'affiliations' : optional_nonempty_string
            }
        },
    'mysql' : {
        'type' : 'dict',
        'excludes' : list(sources - {'mysql'}),
        'required' : True,
        'schema' : {
            'host' : nonempty_string,
            'user' : nonempty_string,
            'passwd' : nonempty_string,
            'port' : { 'type': 'integer' },
            'db' : nonempty_string,
            }
        },

    # An additional CSV with members
    'extra_members' : optional_nonempty_string,

    # Layout options
    'layout' : {
        'type' : 'dict',
        'schema' : { flag : optional_boolean for flag in flags },
        'default' : { flag : True for flag in flags },
        },

    # Default attributes for graphs, nodes, edges, and their subcategories
    'graph_defaults' : dot_defaults('all'),
    'node_defaults' : dot_defaults('all', 'semester', 'unknown', 'member'),
    'edge_defaults' : dot_defaults('all', 'semester', 'unknown'),

    # A mapping of node keys to colors
    'family_colors' : {
        'type' : 'dict',
        'default' : {},
        'keyschema' : nonempty_string,
        'valueschema' : nonempty_string,
        },

    # Custom nodes, each with Graphviz attributes and a semester
    'nodes' : {
            'type' : 'dict',
            'default' : {},
            'keyschema' : nonempty_string,
            'valueschema' : {
                'type' : 'dict',
                'schema' : {
                    'semester' : {
                        'type' : 'string',
                        'coerce' : Semester,
                        },
                    'attributes' : attributes,
                    }
                }
            },

    # Custom edges: Each entry in the list has a list of nodes, which are used
    # to represent a path from which to create edges (which is why there must
    # be at least two nodes in each list). There are also edge attributes
    # applied to all edges in the path.
    'edges' : {
            'type' : 'list',
            'default' : [],
            'schema' : {
                'type' : 'dict',
                'schema' : {
                    'nodes' : {
                        'type' : 'list',
                        'required' : True,
                        'minlength' : 2,
                        'schema' : nonempty_string,
                        },
                    'attributes' : attributes,
                    }
                },
            },

    # Seed for the RNG, to provide consistent output
    'seed': {
        'type' : 'integer',
        'default' : 71,
        }

    })
