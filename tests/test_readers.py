from io import StringIO
import pytest
from snutree.errors import SnutreeReaderError
from snutree.readers import csv, dot, sql

def test_csv_no_error():
    csv_stream = StringIO('"A","B bb B","C"\nx')
    row_generator = csv.get_table(csv_stream)
    next(row_generator)

def test_csv_error():
    csv_stream = StringIO('"A";"B "bb" B";"C"\nx')
    row_generator = csv.get_table(csv_stream)
    with pytest.raises(SnutreeReaderError):
        next(row_generator)

def test_sql_mysql_error():
    with pytest.raises(SnutreeReaderError):
        sql.get_members_local('', {})

def test_sql_ssh_error():
    conf = { 'host' : '', 'port' : 0, 'user' : '', 'private_key' : '' }
    with pytest.raises(SnutreeReaderError):
        sql.get_members_ssh('', conf, conf)

def test_dot_no_error():
    dot_stream = StringIO('digraph { a -> b; }')
    dot.get_table(dot_stream)

def test_dot_error():
    dot_stream = StringIO('digraph { \n a------ \n }')
    with pytest.raises(SnutreeReaderError):
        dot.get_table(dot_stream)

