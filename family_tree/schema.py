from collections import defaultdict
from voluptuous import Invalid, Required, Schema, All, Exclusive, Any, Coerce, DefaultTo, Extra, Length, Optional
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

# TODO determine what to do when there are missing options
source_msg = 'exactly one of {} must be used at a time'.format(['dot', 'csv', 'mysql'])

settings_key_schema = Schema({
    Required(Any('dot', 'csv', 'mysql'), msg=source_msg) : object
    }, extra=True)

settings_data_schema = Schema({
    Required('output') : {
        Required('folder', 'output folder name required') : NonEmptyString,
        Required('name', 'output file name required') : NonEmptyString,
        },
    Exclusive('dot', 'sources', msg=source_msg) : {
        Required('members', 'members DOT file required') : NonEmptyString,
        },
    Exclusive('csv', 'sources', msg=source_msg) : {
        Required('members', 'members CSV required') : NonEmptyString,
        Optional('affiliations', default=None) : Any(NonEmptyString, None),
        },
    Exclusive('mysql', 'sources', msg=source_msg) : {
        Required('host', 'SQL hostname required') : NonEmptyString,
        Required('user', 'SQL user required') : NonEmptyString,
        # TODO handle no password
        Required('passwd', 'SQL password required') : NonEmptyString,
        Required('port', 'SQL server port required') : int,
        Required('db', 'database name required') : NonEmptyString,
        },
    # TODO finish error messages
    Optional('extra_members') : NonEmptyString,
    Required('layout', default=defaultdict(lambda:True)) : All(
        Nullable({
            Optional('semesters') : bool,
            Optional('custom_nodes') : bool,
            Optional('custom_edges') : bool,
            Optional('no_singletons') : bool,
            Optional('family_colors') : bool,
            Optional('unknowns') : bool,
            }),
        Coerce(lambda x : defaultdict(lambda:True, x if x else {})),
        ),
    Optional('nodes', default={}) : Nullable({
        Extra : {
            Required('semester') : All(str, Coerce(Semester)), # Semester can coerce int, but we don't want that in settings
            Optional('attributes', default={}) : Nullable(Attributes),
            }
        }),
    Optional('edges', default=[]) : Nullable([{
        Required('nodes') : All([NonEmptyString], Length(min=2)),
        Optional('attributes', default={}) : Nullable(Attributes)
        }]),
    Required('seed') : int,
    Optional('family_colors', default={}) : Nullable({ Extra : NonEmptyString }),
    Required('edge_defaults') : Defaults('all', 'semester', 'unknown'),
    Required('node_defaults') : Defaults('all', 'semester', 'unknown', 'member'),
    Required('graph_defaults') : Defaults('all'),
    }, required=True, extra=False)

settings_schema = All(settings_key_schema, settings_data_schema)







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

