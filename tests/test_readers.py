from io import StringIO
from unittest import TestCase
from snutree.readers import SnutreeReaderError
import snutree.readers.csv as read_csv
import snutree.readers.sql as read_sql
import snutree.readers.dotread as read_dot

class TestReaders(TestCase):

    def test_csv_no_error(self):

        try:
            csv_stream = StringIO('"A","B bb B","C"\nx')
            row_generator = read_csv.get_table(csv_stream)
            next(row_generator)
        except Exception as e:
            self.fail(f'unexpected CSV read failure:\n{e}')

    def test_csv_error(self):

        csv_stream = StringIO('"A";"B "bb" B";"C"\nx')
        row_generator = read_csv.get_table(csv_stream)
        self.assertRaises(SnutreeReaderError, next, row_generator)

    def test_sql_config_no_error(self):

        try:
            yaml_stream = StringIO('a:\n  b:\n     c:\nx:')
            read_sql.get_configuration(yaml_stream)
        except Exception as e:
            self.fail(f'unexpected SQL read failure:\n{e}')

    def test_sql_config_error(self):

        yaml_stream = StringIO('a:\n  b: "\n   c:')
        self.assertRaises(SnutreeReaderError,
                read_sql.get_configuration, yaml_stream
                )

    def test_sql_mysql_error(self):

        self.assertRaises(SnutreeReaderError,
                read_sql.get_members_local, '', {}
                )

    def test_sql_ssh_error(self):

        conf = {
                'host' : '',
                'port' : 0,
                'user' : '',
                'public_key' : '',
                }

        self.assertRaises(SnutreeReaderError,
                read_sql.get_members_ssh, '', conf, conf
                )

    def test_dot_no_error(self):

        try:
            dot_stream = StringIO('digraph { a -> b; }')
            read_dot.get_table(dot_stream)
        except Exception as e:
            self.fail(f'unexpected DOT read failure:\n{e}')

    def test_dot_error(self):

        dot_stream = StringIO('digraph { \n a------ \n }')
        self.assertRaises(SnutreeReaderError, read_dot.get_table, dot_stream)

