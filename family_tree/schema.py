from cerberus import Validator
from voluptuous import Invalid, Required, Schema, All, Any, DefaultTo, Extra, Length, Optional
from family_tree.entity import Knight, Brother, Candidate, Expelled, KeylessInitiate
from family_tree.semester import Semester

###############################################################################
###############################################################################
#### Custom Validators                                                     ####
###############################################################################
###############################################################################

# Matches nonempty strings
NonEmptyString = All(str, Length(min=1), msg='must be a nonempty string')

# Matches the schema or None. If it matches None, it uses the constructor of
# schema's class without arguments to create a new, presumably empty, object of
# the right type.
Nullable = lambda schema : Any(schema, DefaultTo(type(schema)()))

# Attribute dicts are arbitrary dicts of Graphviz values.
Attributes = {Extra: Any(str, int, float, bool)}

# Matches member types according to the dict, and returns the right constructor
def MemberType(status_string):
    member_status_mapping = {
            'Knight' : Knight,
            'Brother' : Brother,
            'Candidate' : Candidate,
            'Expelled' : Expelled,
            'KeylessInitiate' : KeylessInitiate,
            }
    member_type = member_status_mapping[status_string]
    def validator(string):
        if string == status_string:
            return member_type
        else:
            raise Invalid('status must be one of {{{}}}'.format(', '.join(member_status_mapping.keys())))
    return validator

# Semesters or strings that can be converted to semesters
def SemesterLike(semester_string):
    try:
        return Semester(semester_string)
    except (TypeError, ValueError) as e:
        raise Invalid(str(e))

def Defaults(*categories):
    return { Optional(category) : Attributes for category in categories }

###############################################################################
###############################################################################
#### Custom Validators                                                     ####
###############################################################################
###############################################################################

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

member_schema = Schema(Any(

    {
        Required('status') : MemberType('KeylessInitiate'),
        Required('name') : NonEmptyString,
        Optional('big_name') : Any(None, NonEmptyString),
        Optional('pledge_semester') : SemesterLike,
        },

    {
        Required('status') : MemberType('Knight'),
        Required('badge') : NonEmptyString,
        Required('first_name') : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        Required('last_name') : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : SemesterLike,
        },

    {
        Required('status') : MemberType('Brother'),
        Optional('first_name') : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        Required('last_name') : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : SemesterLike,
        },

    {
        Required('status') : MemberType('Candidate'),
        Required('first_name') : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        Required('last_name') : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : SemesterLike,
        },

    {
        Required('status') : MemberType('Expelled'),
        Required('badge') : NonEmptyString,
        Optional('first_name') : NonEmptyString,
        Optional('preferred_name') : NonEmptyString,
        Optional('last_name') : NonEmptyString,
        Optional('big_badge') : NonEmptyString,
        Optional('pledge_semester') : SemesterLike,
        },

    ), required=True, extra=False)

affiliations_schema = Schema({
    Required('badge') : NonEmptyString,
    Required('chapter_name') : NonEmptyString,
    Required('other_badge') : NonEmptyString,
    })

