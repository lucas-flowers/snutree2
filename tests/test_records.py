import nose.tools as nt
import family_tree.records as rc

def test_combine_names():

    nt.assert_equal(rc.combine_names('Jon', 'Freaking', 'Snow'), 'Freaking Snow')
    nt.assert_equal(rc.combine_names('Jon', 'Jonathan', 'Snow'), 'Jonathan Snow')
    nt.assert_equal(rc.combine_names('Jon', 'Snowy', 'Snow'), 'Jon Snow')
    nt.assert_equal(rc.combine_names('Jon', 'Snowball', 'Snow'), 'Jon Snow')

    # An unfortunate compromise
    nt.assert_equal(rc.combine_names('Samuel', 'Dick', 'Richards'), 'Dick Richards')

    nt.assert_not_equal(rc.combine_names('Jon', 'Snow', 'Snow'), 'Snow Snow')

def test_KnightRecord():

    # No error
    rc.KnightRecord.from_row('9999', 'John', 'Johnny', 'Smith', '8888', 'Fall 1900')
    rc.KnightRecord.from_row('9999', 'John', '', 'Smith', '8888', 'Fall 1900')
    rc.KnightRecord.from_row('9999', 'John', None, 'Smith')

    # # Label
    # nt.assert_equals(
    #         rc.KnightRecord('9999', 'John', None, 'Smith').label(),
    #         'John Smith\\nΔA 9999',
    #         )

    # Badge number padding
    nt.assert_equal(rc.KnightRecord.from_row('1', 'John', None, 'Smith').get_key(), '0001')
    nt.assert_equal(rc.KnightRecord.from_row('-1', 'John', None, 'Smith').get_key(), '-001') # Eh...

    # No big brother
    nt.assert_equals(
            rc.KnightRecord.from_row('9999', 'John', 'Johnny', 'Smith', '', 'Fall 1900').parent,
            None
            )

    # Unfortunately, we do not know whether the semester is needed
    nt.assert_equals(
            rc.KnightRecord.from_row('9999', 'John', 'Johnny', 'Smith', '8888', '').semester,
            None
            )

    # No badge
    nt.assert_raises(rc.RecordError,
            rc.KnightRecord.from_row, '', 'John', 'Johnny', 'Smith', '8888', 'Fall 1900',
            )

    # No first name
    nt.assert_raises(rc.RecordError,
            rc.KnightRecord.from_row, '9999', '', 'Johnny', 'Smith', '8888', 'Fall 1900',
            )

    # No last name
    nt.assert_raises(rc.RecordError,
            rc.KnightRecord.from_row, '9999', 'John', 'Johnny', '', '8888', 'Fall 1900',
            )

    # Malformed big badge
    nt.assert_raises(rc.RecordError,
            rc.KnightRecord.from_row, '9999', 'John', 'Johnny', '', '0x86', 'Fall 1900',
            )

def test_BrotherRecord():

    # In case other tests incremented the ID already
    rc.BrotherRecord.brother_id = 0

    # No error
    rc.BrotherRecord.from_row(None, 'John', 'Johnny', 'Smith').get_key()

    # # Label
    # nt.assert_equals(
    #         rc.BrotherRecord.from_row(None, 'John', 'Johnny', 'Smith').label(),
    #         'Smith\\nΔA Brother',
    #         )

    # Brother ID
    # TODO becomes Brother 2 when label test reenabled
    nt.assert_equal(rc.BrotherRecord.from_row(None, 'John', '', 'Smith').get_key(), 'Brother 1')

    # First and preferred names are optional
    rc.BrotherRecord.from_row(None, '', 'Johnny', 'Smith')
    rc.BrotherRecord.from_row(None, '', '', 'Smith')

    # Has badge
    nt.assert_raises(rc.RecordError,
            rc.BrotherRecord.from_row, '1234', 'John', '', 'Smith'
            )

    # No last name
    nt.assert_raises(rc.RecordError,
            rc.BrotherRecord.from_row, '1234', 'John', '', ''
            )

def test_CandidateRecord():

    # In case other tests incremented the ID already
    rc.CandidateRecord.candidate_id = 0

    # No error
    rc.CandidateRecord.from_row(None, 'John', 'Johnny', 'Smith').get_key()

    # Candidate ID
    nt.assert_equal(rc.CandidateRecord.from_row(None, 'John', '', 'Smith').get_key(), 'Candidate 1')

    # # Label
    # nt.assert_equals(
    #         rc.CandidateRecord.from_row(None, 'John', 'Johnny', 'Smith').label(),
    #         'Johnny Smith\\nΔA Candidate',
    #         )

    # Has badge
    nt.assert_raises(rc.RecordError,
            rc.CandidateRecord.from_row, '1234', 'John', '', 'Smith'
            )

    # No last name
    nt.assert_raises(rc.RecordError,
            rc.CandidateRecord.from_row, '1234', 'John', '', ''
            )

def test_ExpelledRecord():

    # No error
    rc.ExpelledRecord.from_row('1234', 'John', 'Johnny', 'Smith')

    # # Label
    # nt.assert_equals(
    #         rc.ExpelledRecord.from_row('1234', 'John', 'Johnny', 'Smith').label(),
    #         'Member Expelled\\n1234',
    #         )

    # No first name
    nt.assert_raises(rc.RecordError,
            rc.ExpelledRecord.from_row, '9999', '', 'Johnny', 'Smith'
            )

    # No last name
    nt.assert_raises(rc.RecordError,
            rc.ExpelledRecord.from_row, '9999', 'John', 'Johnny', ''
            )

def test_ReaffiliateRecord():

    pass
    # nt.assert_equal(rc.ReaffiliateRecord.from_row(*(), **{}), None)

