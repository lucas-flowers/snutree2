import csv
import networkx as nx
from itertools import chain
from family_tree.records import *

class CsvReader:

    accumulator = dict
    key_name = 'key'

    def __init__(self, rows=None):
        self.rows = rows or []

    def read(self):

        accumulator = self.accumulator()
        row_number = 2
        try:
            for row in self.rows:
                key, fields = self.fields_of(row)
                self.accumulate(accumulator, key, fields)
                row_number += 1
        except:
            raise DirectoryError('Error in row {}'.format(row_number))

        return accumulator

    def fields_of(self, row):
        raise NotImplementedError

    def accumulate(self, accumulator, key, fields):
        if key in accumulator:
            raise DirectoryError('Duplicate {}:  "{}"'.format(self.key_name, key))
        accumulator[key] = fields

    @classmethod
    def from_path(cls, path):
        return cls(list(csv.DictReader(open(path, 'r'))))

    @classmethod
    def from_paths(cls, *paths):
        return cls(chain(*[list(csv.DictReader(open(path, 'r'))) for path in paths]))

class ChapterReader(CsvReader):

    key_name = 'chapter'

    def fields_of(self, row):
        return row['chapter_designation'], row['chapter_location']

class FamilyColorReader(CsvReader):

    key_name = 'family'

    def fields_of(self, row):
        return row['family'], row['color']

class DirectoryReader(CsvReader):

    accumulator = nx.DiGraph
    key_name = 'badge'

    member_record_types = {
            'Active' : KnightRecord,
            'Alumni' : KnightRecord,
            'Brother' : BrotherRecord,
            'Candidate' : CandidateRecord,
            'Expelled' : ExpelledRecord,
            'Reaffiliate' : ReaffiliateRecord, # Returns None
            }

    def __init__(self, rows=None, chapter_locations=None):
        self.chapter_locations = chapter_locations or {}
        super().__init__(rows)

    def fields_of(self, row):

        member_record = self.member_record_types[row['status']].from_row(**row)
        chapter_record = ChapterRecord.from_row(self.chapter_locations, **row)
        reorg_record = ReorganizationRecord.from_row(**row)

        return member_record and member_record.get_key(), (member_record, chapter_record, reorg_record)

    def accumulate(self, accumulator, key, records):

        graph = accumulator
        member_record, chapter_record, reorg_record = records

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

    @classmethod
    def from_paths(cls, chapter_locations=None, *paths):
        reader = super().from_paths(*paths)
        reader.chapter_locations = chapter_locations
        return reader


class DirectoryError(Exception):

    pass

