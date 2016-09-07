import difflib
from family_tree.semester import Semester

class Record:

    badge_format = '{:04d}'

    def __init__(self,
            badge=None,
            first_name=None,
            preferred_name=None,
            last_name=None,
            big_badge=None,
            pledge_semester=None,
            **kwargs):

        self.key = self.read_badge(badge)
        self.name = self.read_name(first_name, preferred_name, last_name)
        self.parent_key = self.read_big_badge(big_badge)
        self.semester = self.read_semester(pledge_semester)

    def read_badge(self, badge):
        try:
            return Record.badge_format.format(int(badge))
        except ValueError:
            raise RecordError('Unexpected badge number: "{}"'.format(badge))

    def read_name(self, first_name, preferred_name, last_name):
        if first_name and last_name:
            return choose_name(first_name, preferred_name, last_name)
        else:
            raise RecordError('Missing first or last name')

    def read_big_badge(self, big_badge):
        if not big_badge:
            return None
        try:
            return Record.badge_format.format(int(big_badge))
        except ValueError:
            raise RecordError('Unexpected big badge number: "{}"'.format(big_badge))

    def read_semester(self, semester):
        # Unfortunately, we will not know if we really needed the semester's
        # value until later
        if not semester:
            return None
        try:
            return Semester(semester)
        except ValueError:
            return None

class KnightRecord(Record):

    pass


class BrotherRecord(Record):

    brother_id = 0

    def read_badge(self, badge):
        if badge:
            raise RecordError('Unknighted brothers do not have badge numbers')
        else:
            BrotherRecord.brother_id += 1
            return 'B{}'.format(BrotherRecord.brother_id - 1)

    def read_name(self, first_name, preferred_name, last_name):
        if last_name:
            return last_name
        else:
            raise RecordError('Missing last name')

class CandidateRecord(Record):

    candidate_id = 0

    def read_badge(self, badge):
        if badge:
            raise RecordError('Candidates do not have badge numbers')
        else:
            CandidateRecord.candidate_id += 1
            return 'C{}'.format(CandidateRecord.candidate_id - 1)

class ExpelledRecord(Record):

    def read_name(self, first_name, preferred_name, last_name):
        # Name is not strictly necessary for this program, but I require it
        if first_name and last_name:
            return 'Member Expelled'
        else:
            raise RecordError('Missing first or last name')

class ReaffiliateRecord:

    def __init__(self, *args, **kwargs):
        self.key = None

def choose_name(first_name, preferred_name, last_name, threshold=.5):
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

