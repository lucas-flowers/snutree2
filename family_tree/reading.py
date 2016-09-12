import csv, sys
import networkx as nx
from networkx.algorithms.operators.binary import union
from family_tree.records import *
from family_tree.tree import *

def read_chapters(path):
    '''
    Arguments
    =========

    path: Location of CSV file with chapter information

    Returns
    =======

    A dict whose keys are chapter designations and whose values are chapter
    locations.

    '''

    chapters = {}
    with open(path, 'r') as f:
        reader = csv.DictReader(f) # TODO check headers
        row_number = 2 # Starts at 2 because the header is Row 1
        try:
            for row in reader:
                chapter_designation = row['chapter_designation']
                chapter_location = row['chapter_location']
                if chapter_designation in chapters:
                    raise DirectoryError('Duplicate chapter: "{}"'.format(chapter_designation))
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

    member_record_types = {
            'Active' : KnightRecord,
            'Alumni' : KnightRecord,
            'Brother' : BrotherRecord,
            'Candidate' : CandidateRecord,
            'Expelled' : ExpelledRecord,
            'Reaffiliate' : ReaffiliateRecord, # Returns None
            }

    with open(path, 'r') as f:

        # TODO check headers
        reader = csv.DictReader(f)
        graph = nx.DiGraph()
        row_number = 2 # Starts at 2 because the header row is Row 1
        try:
            for row in reader:

                # # Create record based on status column
                # record_type = member_record_types[row['status']]
                # record = record_type.from_row(**row)

                record = member_record_types[row['status']].from_row(**row)
                key = record.get_key()

                if key in graph:
                    raise DirectoryError('Duplicate key detected: "{}"'.format(record.key))

                # Implicitly ignores Reaffiliates
                # TODO: Find a way to handle this
                if key:
                    graph.add_node(key, record=record)

                row_number += 1

        except:
            raise DirectoryError('Error in row {}'.format(row_number))

    return graph

def read_transfers(graph, chapters):

    chapter_records = nx.DiGraph()
    for key, node_dict in graph.nodes_iter(data=True):
        record = node_dict['record']
        if record.parent in chapters:
            chapter_record = ChapterRecord.from_member(record, chapters)
            chapter_key = chapter_record.get_key()
            if chapter_key not in chapter_records:
                chapter_records.add_node(chapter_key, record=chapter_record)
            record.parent = chapter_key # Update key to reflect chapter's actual key

    return chapter_records

def read_reorganizations(graph):

    reorg_records = nx.DiGraph()
    for key, node_dict in graph.nodes_iter(data=True):
        record = node_dict['record']
        if hasattr(record, 'refounder_class') and record.refounder_class:
            reorg_record = ReorganizationRecord.from_member(record)
            reorg_key = reorg_record.get_key()
            if reorg_key not in reorg_records:
                reorg_records.add_node(reorg_key, record=reorg_record)
            record.refounder_class = reorg_key # Update key to reflect reorg's actual key

    return reorg_records


def read(directory_path, chapter_path, bnks_path):

    chapters = read_chapters(chapter_path)

    graph = read_members(directory_path) # Read all normal members
    graph = union(graph, read_members(bnks_path)) # Add brothers not Knights
    graph = union(graph, read_transfers(graph, chapters)) # Add transfer chapters
    graph = union(graph, read_reorganizations(graph)) # Add reorganizations

    return graph


class DirectoryError(Exception):

    pass

