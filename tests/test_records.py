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

def test_ReorganizationRecord():

    # Label
    assert_equals(ReorganizationRecord('Fall 1922').label(), 'Reorganization')

    # TODO should reorganization require a semester name?
    # ReorganizationRecord()

def test_ChapterRecord():

    # No error
    ChapterRecord('KΔ', 'Doo-Kez-Nee', 'Fall 1942')
    ChapterRecord('KΔ', 'Doo-Kez-Nee')

    # Key
    assert_equals(
            ChapterRecord('ΔZ', 'WRC', 'Fall 2333').key,
            'ΔZ (Fall 2333)',
            )

    # Key, again (TODO I don't like how this is allowed)
    assert_equals(
            ChapterRecord('ΔZ', 'WRC').key,
            'ΔZ (None)',
            )

    # Label
    assert_equals(
            ChapterRecord('ΔZ', 'WRC').label(),
            'ΔZ Chapter\nWRC',
            )

    # Name
    assert_equals(
            ChapterRecord('ΔZ', 'WRC').name,
            'WRC',
            )

    # Missing designation
    assert_raises(
            RecordError,
            ChapterRecord, '', 'Doo-Kez-Nee',
            )

    # Missing name
    assert_raises(
            RecordError,
            ChapterRecord, 'KΔ',
            )

def test_KnightRecord():

    # No error
    KnightRecord('9999', 'John', 'Johnny', 'Smith', '8888', 'Fall 1900')
    KnightRecord('9999', 'John', '', 'Smith', '8888', 'Fall 1900')
    KnightRecord('9999', 'John', None, 'Smith')

    # Label
    assert_equals(
            KnightRecord('9999', 'John', None, 'Smith').label(),
            'John Smith\nΔA 9999',
            )

    # Badge number padding
    assert_equal(KnightRecord('1', 'John', None, 'Smith').key, '0001')
    assert_equal(KnightRecord('-1', 'John', None, 'Smith').key, '-001') # Eh...

    # No big brother
    assert_equals(
            KnightRecord('9999', 'John', 'Johnny', 'Smith', '', 'Fall 1900').parent_keys,
            []
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

    # In case other tests incremented the ID already
    BrotherRecord.brother_id = 0

    # No error
    BrotherRecord(None, 'John', 'Johnny', 'Smith')

    # Label
    assert_equals(
            BrotherRecord(None, 'John', 'Johnny', 'Smith').label(),
            'Smith\nΔA Brother',
            )

    # Brother ID
    assert_equal(BrotherRecord(None, 'John', '', 'Smith').key, 'B2')

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

def test_CandidateRecord():

    # In case other tests incremented the ID already
    CandidateRecord.candidate_id = 0

    # No error
    CandidateRecord(None, 'John', 'Johnny', 'Smith')

    # Candidate ID
    assert_equal(CandidateRecord(None, 'John', '', 'Smith').key, 'C1')

    # Label
    assert_equals(
            CandidateRecord(None, 'John', 'Johnny', 'Smith').label(),
            'Johnny Smith\nΔA Candidate',
            )

    # Has badge
    assert_raises(RecordError,
            CandidateRecord, '1234', 'John', '', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            CandidateRecord, '1234', 'John', '', ''
            )

def test_ExpelledRecord():

    # No error
    ExpelledRecord('1234', 'John', 'Johnny', 'Smith')

    # Label
    assert_equals(
            ExpelledRecord('1234', 'John', 'Johnny', 'Smith').label(),
            'Member Expelled\n1234',
            )

    # No first name
    assert_raises(RecordError,
            ExpelledRecord, '9999', '', 'Johnny', 'Smith'
            )

    # No last name
    assert_raises(RecordError,
            ExpelledRecord, '9999', 'John', 'Johnny', ''
            )

def test_ReaffiliateRecord():

    assert_equal(ReaffiliateRecord(*(), **{}).name, NotImplemented)

