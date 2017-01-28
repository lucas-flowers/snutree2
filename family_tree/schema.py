from voluptuous import Invalid, Required, Schema, All, Any, Length, Optional
from family_tree.entity import Knight, Brother, Candidate, Expelled, KeylessInitiate
from family_tree.semester import Semester

# Here we use voluptuous instead of cerberus because cerberus was *very* slow
# with this schema. (I think it had to to with its string-based options, and
# the fact that it appears not to be focused on /lists/ of dictionaries.)

###############################################################################
###############################################################################
#### Utilities                                                             ####
###############################################################################
###############################################################################

# Matches nonempty strings
NonEmptyString = All(str, Length(min=1), msg='must be a nonempty string')

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

###############################################################################
###############################################################################
#### Schema                                                                ####
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

