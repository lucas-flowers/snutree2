from nose.tools import *
from family_tree.records import *
from family_tree.semester import Semester

def test_choose_name():

    assert_equal(choose_name('Jon', 'Freaking', 'Snow'), 'Freaking Snow')
    assert_equal(choose_name('Jon', 'Jonathan', 'Snow'), 'Jonathan Snow')
    assert_equal(choose_name('Jon', 'Snowy', 'Snow'), 'Jon Snow')
    assert_equal(choose_name('Jon', 'Snowball', 'Snow'), 'Jon Snow')

    # An unfortunate compromise
    assert_equal(choose_name('Samuel', 'Dick', 'Richards'), 'Dick Richards')

    assert_not_equal(choose_name('Jon', 'Snow', 'Snow'), 'Snow Snow')

def test_KnightRecord():

    # No error
    KnightRecord('9999', 'John', 'Johnny', 'Smith', '8888', 'Fall 1900')
    KnightRecord('9999', 'John', '', 'Smith', '8888', 'Fall 1900')
    KnightRecord('9999', 'John', None, 'Smith')

    # Badge number padding
    assert_equal(KnightRecord('1', 'John', None, 'Smith').key, '0001')
    assert_equal(KnightRecord('-1', 'John', None, 'Smith').key, '-001') # Eh...

    # No big brother
    assert_equals(
            KnightRecord('9999', 'John', 'Johnny', 'Smith', '', 'Fall 1900').parent_key,
            None
            )

    # Unfortunately, we do not know whether the semester is needed
    assert_equals(
            KnightRecord('9999', 'John', 'Johnny', 'Smith', '8888', '').semester,
            None
            )

    # No badge
    assert_raises(RecordError,
            KnightRecord, '', 'John', 'Johnny', 'Smith', '8888', 'Fall 1900',
            )

    # No first name
    assert_raises(RecordError,
            KnightRecord, '9999', '', 'Johnny', 'Smith', '8888', 'Fall 1900',
            )

    # No last name
    assert_raises(RecordError,
            KnightRecord, '9999', 'John', 'Johnny', '', '8888', 'Fall 1900',
            )

    # Malformed big badge
    assert_raises(RecordError,
            KnightRecord, '9999', 'John', 'Johnny', '', '0x86', 'Fall 1900',
            )

def test_BrotherRecord():

    # No error
    BrotherRecord(None, 'John', 'Johnny', 'Smith')

    # First and preferred names are optional
    BrotherRecord(None, '', 'Johnny', 'Smith')
    BrotherRecord(None, '', '', 'Smith')

    # Has badge
    assert_raises(RecordError,
            BrotherRecord, '1234', 'John', '', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            BrotherRecord, '1234', 'John', '', ''
            )

    # Brother ID
    assert_equal(BrotherRecord(None, 'John', '', 'Smith').key, 'B3')

def test_CandidateRecord():

    # No error
    CandidateRecord(None, 'John', 'Johnny', 'Smith')

    # Has badge
    assert_raises(RecordError,
            CandidateRecord, '1234', 'John', '', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            CandidateRecord, '1234', 'John', '', ''
            )

    # Candidate ID
    assert_equal(CandidateRecord(None, 'John', '', 'Smith').key, 'C1')

def test_ExpelledRecord():

    # No error
    ExpelledRecord('1234', 'John', 'Johnny', 'Smith')

    # No first name
    assert_raises(RecordError,
            ExpelledRecord, '9999', '', 'Johnny', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            ExpelledRecord, '9999', 'John', 'Johnny', ''
            )

def test_ReaffiliateRecord():

    assert_equal(ReaffiliateRecord(*(), **{}).key, None)

