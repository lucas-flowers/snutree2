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

