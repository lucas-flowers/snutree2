from nose.tools import *
from family_tree.records import *
from family_tree.semester import Semester

def test_combine_names():

    assert_equal(combine_names('Jon', 'Freaking', 'Snow'), 'Freaking Snow')
    assert_equal(combine_names('Jon', 'Jonathan', 'Snow'), 'Jonathan Snow')
    assert_equal(combine_names('Jon', 'Snowy', 'Snow'), 'Jon Snow')
    assert_equal(combine_names('Jon', 'Snowball', 'Snow'), 'Jon Snow')

    # An unfortunate compromise
    assert_equal(combine_names('Samuel', 'Dick', 'Richards'), 'Dick Richards')

    assert_not_equal(combine_names('Jon', 'Snow', 'Snow'), 'Snow Snow')

def test_ReorganizationRecord():

    # # Label
    # assert_equals(ReorganizationRecord('Fall 1922').label(), 'Reorganization')

    row = {'refounder_class' : 'Fall 1945'}

    # The placement semester for Reorganization nodes is one semester before
    # the refounder_class field...
    assert_equals(
            ReorganizationRecord.from_row(**row).semester,
            Semester('Spring 1945'),
            )

    # ... however, the actual key for the reorganization is of the true
    # reorganization semester.
    assert_equals(
            ReorganizationRecord.from_row(**row).get_key(),
            'Reorganization Node Fall 1945',
            )

def test_ChapterRecord():

    row1 = {
            'name' : 'John Doe',
            'pledge_semester' : 'Fall 1942',
            'big_badge' : 'ΔZ',
            }

    row2 = {
            'name' : 'John Smith',
            'pledge_semester' : 'Fall 1945',
            'big_badge' :'KΔ',
            }

    chapter_locations = {
            'KΔ' : 'Doo-Kez-Nee',
            'ΔZ' : 'WRC',
            }


    # No error
    ChapterRecord.from_row(chapter_locations, **row1)

    # Key
    assert_equals(
            ChapterRecord.from_row(chapter_locations, **row1).get_key(),
            'ΔZ Spring 1942',
            )

    # # Label
    # assert_equals(
    #         ChapterRecord('ΔZ', 'WRC').label(),
    #         'ΔZ Chapter\\nWRC',
    #         )

    # Name
    assert_equals(
            ChapterRecord.from_row(chapter_locations, **row2).location,
            'Doo-Kez-Nee',
            )

def test_KnightRecord():

    # No error
    KnightRecord.from_row('9999', 'John', 'Johnny', 'Smith', '8888', 'Fall 1900')
    KnightRecord.from_row('9999', 'John', '', 'Smith', '8888', 'Fall 1900')
    KnightRecord.from_row('9999', 'John', None, 'Smith')

    # # Label
    # assert_equals(
    #         KnightRecord('9999', 'John', None, 'Smith').label(),
    #         'John Smith\\nΔA 9999',
    #         )

    # Badge number padding
    assert_equal(KnightRecord.from_row('1', 'John', None, 'Smith').get_key(), '0001')
    assert_equal(KnightRecord.from_row('-1', 'John', None, 'Smith').get_key(), '-001') # Eh...

    # No big brother
    assert_equals(
            KnightRecord.from_row('9999', 'John', 'Johnny', 'Smith', '', 'Fall 1900').parent,
            None
            )

    # Unfortunately, we do not know whether the semester is needed
    assert_equals(
            KnightRecord.from_row('9999', 'John', 'Johnny', 'Smith', '8888', '').semester,
            None
            )

    # No badge
    assert_raises(RecordError,
            KnightRecord.from_row, '', 'John', 'Johnny', 'Smith', '8888', 'Fall 1900',
            )

    # No first name
    assert_raises(RecordError,
            KnightRecord.from_row, '9999', '', 'Johnny', 'Smith', '8888', 'Fall 1900',
            )

    # No last name
    assert_raises(RecordError,
            KnightRecord.from_row, '9999', 'John', 'Johnny', '', '8888', 'Fall 1900',
            )

    # Malformed big badge
    assert_raises(RecordError,
            KnightRecord.from_row, '9999', 'John', 'Johnny', '', '0x86', 'Fall 1900',
            )

def test_BrotherRecord():

    # In case other tests incremented the ID already
    BrotherRecord.brother_id = 0

    # No error
    BrotherRecord.from_row(None, 'John', 'Johnny', 'Smith').get_key()

    # # Label
    # assert_equals(
    #         BrotherRecord.from_row(None, 'John', 'Johnny', 'Smith').label(),
    #         'Smith\\nΔA Brother',
    #         )

    # Brother ID
    # TODO becomes Brother 2 when label test reenabled
    assert_equal(BrotherRecord.from_row(None, 'John', '', 'Smith').get_key(), 'Brother 1')

    # First and preferred names are optional
    BrotherRecord.from_row(None, '', 'Johnny', 'Smith')
    BrotherRecord.from_row(None, '', '', 'Smith')

    # Has badge
    assert_raises(RecordError,
            BrotherRecord.from_row, '1234', 'John', '', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            BrotherRecord.from_row, '1234', 'John', '', ''
            )

def test_CandidateRecord():

    # In case other tests incremented the ID already
    CandidateRecord.candidate_id = 0

    # No error
    CandidateRecord.from_row(None, 'John', 'Johnny', 'Smith').get_key()

    # Candidate ID
    assert_equal(CandidateRecord.from_row(None, 'John', '', 'Smith').get_key(), 'Candidate 1')

    # # Label
    # assert_equals(
    #         CandidateRecord.from_row(None, 'John', 'Johnny', 'Smith').label(),
    #         'Johnny Smith\\nΔA Candidate',
    #         )

    # Has badge
    assert_raises(RecordError,
            CandidateRecord.from_row, '1234', 'John', '', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            CandidateRecord.from_row, '1234', 'John', '', ''
            )

def test_ExpelledRecord():

    # No error
    ExpelledRecord.from_row('1234', 'John', 'Johnny', 'Smith')

    # # Label
    # assert_equals(
    #         ExpelledRecord.from_row('1234', 'John', 'Johnny', 'Smith').label(),
    #         'Member Expelled\\n1234',
    #         )

    # No first name
    assert_raises(RecordError,
            ExpelledRecord.from_row, '9999', '', 'Johnny', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            ExpelledRecord.from_row, '9999', 'John', 'Johnny', ''
            )

def test_ReaffiliateRecord():

    pass
    # assert_equal(ReaffiliateRecord.from_row(*(), **{}), None)

