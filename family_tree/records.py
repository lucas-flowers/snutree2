import difflib
from family_tree.semester import Semester

class MemberRecord:

    badge_format = '{:04d}'

    def __init__(self,
            name=None,
            pledge_semester=None,
            big_badge=None,
            refounder_class=None,
            ):
        self.name = name
        self.pledge_semester = pledge_semester
        self.big_badge = big_badge
        self.refounder_class = refounder_class

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
            refounder_class=None,
            **rest):
        '''
        Arguments
        =========

        A **dict representing the fields in a row of the directory. All fields
        are *strings* that have not yet been validated.

        Returns
        =======

        A tuple, (key, record):

        key: Key for the record
        record: The record

        '''

        record = cls()

        key = record.get_key_from_badge(badge)

        record.name_from_row(first_name, preferred_name, last_name)
        record.semester_from_row(pledge_semester)
        record.big_badge_from_row(big_badge);
        record.refounder_class_from_row(refounder_class)

        return key, record

    def get_key_from_badge(self, badge_string):
        try:
            return self.badge_format.format(int(badge_string))
        except ValueError:
            raise RecordError('Unexpected badge number: "{}"'.format(badge_string))

    def name_from_row(self, first_name, preferred_name, last_name):
        if first_name and last_name:
            self.name = combine_names(first_name, preferred_name, last_name)
        else:
            raise RecordError('Missing first or last name')

    def semester_from_row(self, semester_string):
        # We will not know if we really need the semester's value until later
        if not semester_string:
            self.semester = None
        else:
            try:
                self.semester = Semester(semester_string)
            except (TypeError, ValueError):
                raise RecordError('Invalid semester: "{}"'.format(semester_string))

    def big_badge_from_row(self, big_badge_string):
        if not big_badge_string:
            self.big_badge = None
        else:
            try:
                self.big_badge = self.badge_format.format(int(big_badge_string))
            except ValueError:
                # The big's badge is not an integer; it may be a chapter designation
                self.big_badge = big_badge_string

    def refounder_class_from_row(self, refounder_class_string):
        if refounder_class_string:
            try:
                self.refounder_class = Semester(refounder_class_string)
            except (TypeError, ValueError):
                raise RecordError('Unexpected refounding semester: "{}"'
                        .format(refounder_class_string))
        else:
            self.refounder_class = None

class KnightRecord(MemberRecord):

    pass

class BrotherRecord(MemberRecord):

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    brother_id = 0

    def get_key_from_badge(self, badge_string):
        if badge_string:
            raise RecordError('Unknighted brothers do not have badge numbers')
        else:
            key = 'Brother {}'.format(BrotherRecord.brother_id)
            BrotherRecord.brother_id += 1
            return key

    def name_from_row(self, first_name, preferred_name, last_name):
        if last_name:
            self.name = last_name
        else:
            return RecordError('Missing last name')

class CandidateRecord(MemberRecord):

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    candidate_id = 0

    def get_key_from_badge(self, badge_string):
        if badge_string:
            raise RecordError('Candidates do not have badge numbers')
        else:
            key = 'Candidate {}'.format(CandidateRecord.candidate_id)
            CandidateRecord.candidate_id += 1
            return key

class ExpelledRecord(MemberRecord):

    ###########################################################################
    #### Row Validation Functions                                          ####
    ###########################################################################

    def name_from_row(self, first_name, preferred_name, last_name):
        if first_name and last_name:
            # They *should* have a name, but it's not going to be displayed
            self.name = 'Member Expelled'
        else:
            raise RecordError('Missing first or last name')




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
