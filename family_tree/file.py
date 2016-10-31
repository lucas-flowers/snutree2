import csv, yaml
import networkx as nx
from itertools import chain
from family_tree.records import *

class SettingsReader:

    def __init__(self, settings=None):
        self.settings = settings or ''

    def read(self):
        return yaml.load(self.settings)

    @classmethod
    def from_path(cls, path):
        with open(path, 'r') as f:
            return cls(f.read())

class CsvReader:

    accumulator = dict

    def __init__(self, rows=None):
        self.rows = rows or []

    def read(self):

        accumulator = self.accumulator()
        row_number = 2
        try:
            for row in self.rows:
                self.accumulate(accumulator, row)
                row_number += 1
        except:
            raise DirectoryError('Error in row {}'.format(row_number))

        return accumulator

    def accumulate(self, accumulator, key, fields):
        raise NotImplementedError

    @classmethod
    def from_path(cls, path):
        with open(path, 'r') as f:
            return cls(list(csv.DictReader(f)))

class SimpleReader(CsvReader):

    key_name = NotImplemented

    def fields_of(self, row):
        raise NotImplementedError

    def accumulate(self, accumulator, row):
        key, fields = self.fields_of(row)
        if key in accumulator:
            raise DirectoryError('Duplicate {}:  "{}"'.format(self.key_name, key))
        accumulator[key] = fields

class ChapterReader(SimpleReader):

    key_name = 'chapter'

    def fields_of(self, row):
        return row['chapter_designation'], row['chapter_location']

class DirectoryReader(CsvReader):

    accumulator = nx.DiGraph

    def __init__(self, rows=None, chapter_locations=None):
        self.chapter_locations = chapter_locations or {}
        super().__init__(rows)

    def accumulate(self, accumulator, row):
        # TODO move member/chapter/reorg functions into separate classes, with
        # a general abstract class over all of them

        graph = accumulator

        member_record = MemberRecord.from_row(**row)
        chapter_record = ChapterRecord.from_row(self.chapter_locations, **row)
        reorg_record = ReorganizationRecord.from_row(**row)

        if member_record:
            member_key = member_record.get_key()
            if member_key in graph and 'record' in graph.node[member_key]:
                raise DirectoryError('Duplicate badge: "{}"'.format(member_key))
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

        # Invalid parent badge
        # TODO move to inside or beside the loop in tree.FamilyTree.validate_node_existence?
        # (potentially helping with the other TODO for this accumulate function)
        if member_record and not member_record.parent and row['big_badge'] and not chapter_record:
            raise DirectoryError('Invalid big brother badge or transfer chapter designation: "{}"'.format(row['big_badge']))


    @classmethod
    def from_path(cls, directory_path, chapter_locations=None):
        reader = super().from_path(directory_path)
        reader.chapter_locations = chapter_locations
        return reader


class DirectoryError(Exception):

    pass

