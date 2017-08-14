from io import StringIO
from unittest import TestCase
from snutree import SnutreeReaderError
from snutree.readers import csv, dot, sql

class TestReaders(TestCase):

    def test_csv_no_error(self):

        try:
            csv_stream = StringIO('"A","B bb B","C"\nx')
            row_generator = csv.get_table(csv_stream)
            next(row_generator)
        except SnutreeReaderError as e:
            self.fail(f'unexpected CSV read failure:\n{e}')

    def test_csv_error(self):

        csv_stream = StringIO('"A";"B "bb" B";"C"\nx')
        row_generator = csv.get_table(csv_stream)
        self.assertRaises(SnutreeReaderError, next, row_generator)

    def test_sql_mysql_error(self):

        self.assertRaises(SnutreeReaderError,
                sql.get_members_local, '', {}
                )

    def test_sql_ssh_error(self):

        conf = {
                'host' : '',
                'port' : 0,
                'user' : '',
                'public_key' : '',
                }

        self.assertRaises(SnutreeReaderError,
                sql.get_members_ssh, '', conf, conf
                )

    def test_dot_no_error(self):

        try:
            dot_stream = StringIO('digraph { a -> b; }')
            dot.get_table(dot_stream)
        except SnutreeReaderError as e:
            self.fail(f'unexpected DOT read failure:\n{e}')

    def test_dot_error(self):

        dot_stream = StringIO('digraph { \n a------ \n }')
        self.assertRaises(SnutreeReaderError, dot.get_table, dot_stream)

