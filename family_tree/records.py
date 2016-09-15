import difflib
from collections import defaultdict
from family_tree.color import ColorChooser
from family_tree.semester import Semester

def member_record_from_row(row):
    '''
    A factory.
    '''

    classes = {
            'Active' : KnightRecord,
            'Alumni' : KnightRecord,
            'Brother' : BrotherRecord,
            'Candidate' : CandidateRecord,
            'Expelled' : ExpelledRecord,
            'Reaffiliate' : ReaffiliateRecord, # Returns None
            }

    return classes[row['status']].from_row(**row)

class Record:

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def validate_row_semester(cls, semester_string):
        # We will not know if we really need the semester's value until later
        try:
            return Semester(semester_string)
        except (TypeError, ValueError):
            return None

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def dot_node_attributes(self):
        return {}

    def dot_edge_attributes(self, other):
        return {}

class ReorganizationRecord(Record):

    def __init__(self, semester=None):

        self.semester = semester

    def get_key(self):

        # Plus one because self.semester is the placement semester, not the
        # true semester
        return 'Reorganization Node {}'.format(self.semester+1)

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def from_row(cls,
            refounder_class=None,
            **rest):

        if refounder_class:

            record = cls()

            # Minus one because the Reorganization node is placed a semester
            # before the actual reorganization (so that it is above the new
            # refounders).
            record.semester = cls.validate_row_refounder_class(refounder_class) - 1

            return record

        else:

            return None

    @classmethod
    def validate_row_refounder_class(cls, refounder_class_string):
        try:
            return Semester(refounder_class_string)
        except (TypeError, ValueError):
            raise RecordError('Unexpected refounding semester: "{}"'
                    .format(refounder_class_string))

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def dot_node_attributes(self):
        return {
                'label' : 'Reorganization',
                'shape' : 'oval'
                }

    def dot_edge_attributes(self, other):
        if self.semester > other.semester:
            return {'style' : 'dashed'}
        else:
            return {}

class ChapterRecord(Record):

    def __init__(self,
            semester=None,
            designation=None,
            location=None
            ):

        self.semester = semester
        self.designation = designation
        self.location = location

    def get_key(self):
        return '{} {}'.format(self.designation, self.semester)

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def from_row(cls, chapters,
            pledge_semester=None,
            big_badge=None,
            **rest):

        if big_badge and big_badge in chapters:

            record = cls()

            record.semester = cls.validate_row_semester(pledge_semester) - 1
            record.designation = big_badge # No validation; assumed already checked
            record.location = chapters[record.designation]

            return record

        else:

            return None

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def dot_node_attributes(self):
        return {
                'label' : '{} Chapter\\n{}'.format(self.designation, self.location),
                'color' : 'none',
                'fillcolor' : 'none',
                }

    def dot_edge_attributes(self, other):
        return {'style' : 'dashed'}

class MemberRecord(Record):

    badge_format = '{:04d}'
    color_chooser = ColorChooser.from_graphviz_colors()
    family_colors = defaultdict(color_chooser.next_color)

    def __init__(self,
            name=None,
            pledge_semester=None,
            big_badge=None,
            badge=None,
            ):
        self.name = name
        self.semester = pledge_semester
        self.parent = big_badge
        self.badge = badge

    def get_key(self):
        raise NotImplementedError

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def from_row(cls,
            badge=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            **rest):
        '''
        Arguments
        =========

        A **dict representing the fields in a row of the directory. All fields
        are *strings* that have not yet been validated.

        Returns
        =======

        record: The record

        '''

        record = cls()

        record.badge = cls.validate_row_badge(badge)
        record.name = cls.validate_row_name(first_name, preferred_name, last_name)
        record.semester = cls.validate_row_semester(pledge_semester)
        record.parent = cls.validate_row_parent(big_badge);

        return record

    @classmethod
    def validate_row_badge(cls, badge_string):
        try:
            return cls.badge_format.format(int(badge_string))
        except ValueError:
            raise RecordError('Unexpected badge number: "{}"'.format(badge_string))

    @classmethod
    def validate_row_name(cls, first_name, preferred_name, last_name):
        if first_name and last_name:
            return combine_names(first_name, preferred_name, last_name)
        else:
            raise RecordError('Missing first or last name')

    @classmethod
    def validate_row_parent(cls, big_badge_string):
        if big_badge_string:
            try:
                return cls.badge_format.format(int(big_badge_string))
            except ValueError:
                # The big's badge is not an integer; it may be a chapter designation
                pass
        return None

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def get_dot_label(self):
        return ''

    def dot_node_attributes(self):
        return {
                'label' : self.get_dot_label(),
                'color' : self.family_colors[self.family],
                }

class KnightRecord(MemberRecord):

    def get_key(self):
        return self.badge

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def get_dot_label(self):
        return '{}\\nΔA {}'.format(self.name, self.badge)

class BrotherRecord(MemberRecord):

    brother_id = 0

    def __init__(self, **kwargs):
        self.key = 'Brother {}'.format(BrotherRecord.brother_id)
        BrotherRecord.brother_id += 1
        super().__init__(**kwargs)

    def get_key(self):
        return self.key

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def validate_row_badge(cls, badge_string):
        if badge_string:
            raise RecordError('Unknighted brothers do not have badge numbers')
        else:
            return None

    @classmethod
    def validate_row_name(cls, first_name, preferred_name, last_name):
        if last_name:
            return last_name
        else:
            return RecordError('Missing last name')

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def get_dot_label(self):
        return '{}\\nΔA Brother'.format(self.name)

class CandidateRecord(MemberRecord):

    candidate_id = 0

    def __init__(self, **kwargs):
        self.key = 'Candidate {}'.format(CandidateRecord.candidate_id)
        CandidateRecord.candidate_id += 1
        super().__init__(**kwargs)

    def get_key(self):
        return self.key

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def validate_row_badge(cls, badge_string):
        if badge_string:
            raise RecordError('Candidates do not have badge numbers')
        else:
            return None

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def get_dot_label(self):
        return '{}\\nΔA Candidate'.format(self.name)

class ExpelledRecord(KnightRecord):

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def validate_row_name(cls, first_name, preferred_name, last_name):
        if first_name and last_name:
            # They *should* have a name, but it's not going to be displayed
            return 'Member Expelled'
        else:
            raise RecordError('Missing first or last name')

    ###########################################################################
    #### DOT Functions                                                     ####
    ###########################################################################

    def get_dot_label(self):
        return '{}\\n{}'.format(self.name, self.badge)

# TODO use affiliate list to do stuff
class ReaffiliateRecord(MemberRecord):

    def get_key(self):
        return None

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    @classmethod
    def from_row(cls, **kwargs):
        return None

def combine_names(first_name, preferred_name, last_name, threshold=.5):
    '''
    Arguments
    =========

    first: First name
    preferred: Preferred name
    last: Last name
    threshold: The distance threshold used to determine similarity

    Returns
    =======

    "[preferred] [last]" if the `preferred` is not too similar to `last`
    "[first] [last]" if `preferred` is too similar to `last`

    Notes
    =====

    This might provide a marginally incorrect name for those who
       a. go by something other than their first name that
       b. is similar to their last name,
    but otherwise it should almost always[^almost] provide something reasonable.

    The whole point here is to
       a. avoid using *only* last names on the tree, while
       b. using the "first" names brothers actually go by, and while
       c. avoiding using a first name that is a variant of the last name.

    [^almost]: I say "almost always" because, for example, someone with the
    last name "Richards" who goes by "Dick" will be listed incorrectly as "Dick
    Richards" even if his other names are neither Dick nor Richard (unless the
    tolerance threshold is made very low).
    '''

    if preferred_name and difflib.SequenceMatcher(None, preferred_name, last_name).ratio() < threshold:
        return '{} {}'.format(preferred_name, last_name)
    else:
        return '{} {}'.format(first_name, last_name)

class RecordError(Exception):

    pass
