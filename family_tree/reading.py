import csv, sys
from family_tree.records import *
from family_tree.node import *

member_record_types = {
        'Active' : KnightRecord,
        'Alumni' : KnightRecord,
        'Brother' : BrotherRecord,
        'Candidate' : CandidateRecord,
        'Expelled' : ExpelledRecord,
        'Reaffiliate' : ReaffiliateRecord, # Returns None
        }

def read_chapters(path):
    '''
    Arguments
    =========

    path: Location of CSV file with chapter information

    Returns
    =======

    A dict whose keys are chapter designations and whose values are chapter
    names.

    '''

    with open(path, 'r') as f:
        reader = csv.DictReader(f) # TODO check headers
        chapters = {}
        row_number = 2 # Starts at 2 because the header is Row 1
        try:
            for row in reader:
                chapter_designation = row['chapter_designation']
                chapter_location = row['chapter_location']
                if chapter_designation in chapters:
                    raise DirectoryError('Duplicate chapter detected: "{}"'.format(chapter_designation))
                chapters[chapter_designation] = chapter_location
                row_number += 1
        except:
            raise DirectoryError('Error in row {}'.format(row_number))

    return chapters

def read_members(path):
    '''
    Arguments
    =========

    path: Location of CSV file with directory information

    Returns
    =======

    A dict of records. One record for each member in the directory (not
    including reaffiliates).

    '''

    with open(path, 'r') as f:

        # TODO check headers
        reader = csv.DictReader(f)
        records = {}
        row_number = 2 # Starts at 2 because the header row is Row 1
        try:
            for row in reader:

                # Create record based on status column
                record = member_record_types[row['status']](**row)

                # Ignore the record if the constructor returned None (i.e., it
                # was a Reaffiliate)
                if record:

                    if record.key in records:
                        raise DirectoryError('Duplicate key detected: "{}"'.format(record.key))

                    records[record.key] = record

                row_number += 1

        except:
            raise DirectoryError('Error in row {}'.format(row_number))

    return records


def read(directory_path, chapter_path, bnks_path):

    raise NotImplementedError

    chapters = read_chapters(chapter_path)

    records = read_members(directory_path)
    brothers_not_knights = read_members(bnks_path)
    records.update(brothers_not_knights)



class DirectoryError(Exception):

    pass

