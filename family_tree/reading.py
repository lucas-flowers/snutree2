import csv, sys
import networkx as nx
from networkx.algorithms.operators.binary import union
from networkx.algorithms.operators.all import compose_all
from family_tree.records import *
from family_tree.tree import *

def csv_to_list(path):
    with open(path, 'r') as f:
        dict_list = list(csv.DictReader(f))
    return dict_list

def read_chapters(chapter_list):

    chapters = {}
    row_number = 2 # Starts at 2 because the header is Row 1
    try:
        for row in chapter_list:
            designation = row['chapter_designation']
            location = row['chapter_location']
            if designation in chapters:
                raise DirectoryError('Duplicate chapter: "{}"'.format(designation))
            chapters[designation] = location
            row_number += 1
    except:
        raise DirectoryError('Error in row {}'.format(row_number))

    return chapters

def read_graph(member_list, chapter_locations):

    member_record_types = {
            'Active' : KnightRecord,
            'Alumni' : KnightRecord,
            'Brother' : BrotherRecord,
            'Candidate' : CandidateRecord,
            'Expelled' : ExpelledRecord,
            'Reaffiliate' : ReaffiliateRecord, # Returns None
            }

    graph = nx.DiGraph()
    row_number = 2 # Starts at 2 because the header is Row 1
    for row in member_list:

        # TODO simplify by restructuring MemberRecord and subclasses. Stuff
        # like moving the record_types dict to teh records module. The goal
        # isto make it look as simple as the chapter/reorg from_row calls.
        member_record = member_record_types[row['status']].from_row(**row)
        chapter_record = ChapterRecord.from_row(chapter_locations, **row)
        reorg_record = ReorganizationRecord.from_row(**row)

        # TODO avoid re-adding chapter/reorg/etc. nodes with multiple children

        if member_record:
            member_key = member_record.get_key()
            graph.add_node(member_key, record=member_record)
            if member_record.parent:
                graph.add_edge(member_record.parent, member_key)

        if chapter_record:
            chapter_key = chapter_record.get_key()
            if chapter_key not in graph:
                graph.add_node(chapter_key, record=chapter_record)
            graph.add_edge(chapter_key, member_key)

        if reorg_record:
            reorg_key = reorg_record.get_key()
            if reorg_key not in graph:
                graph.add_node(reorg_key, record=reorg_record)
            graph.add_edge(reorg_key, member_key)

    for key, node_dict in graph.nodes_iter(data=True):
        if 'record' not in node_dict:
            # TODO fill this error
            raise DirectoryError('TODO')

    return graph


def read(directory_path, chapter_path, bnks_path):

    chapter_locations = read_chapters(csv_to_list(chapter_path))

    # TODO be sure to provide error information errors correctly, or probably
    # split this into two calls---one for each file
    member_list = csv_to_list(directory_path) + csv_to_list(bnks_path)

    # TODO add options?
    graph = read_graph(member_list, chapter_locations)

    return graph


class DirectoryError(Exception):

    pass

