from io import BytesIO
import pytest
from snutree.errors import SnutreeReaderError
from snutree.readers import csv, dot, sql, json

def test_csv_no_error():
    csv_stream = BytesIO(b'"A","B bb B","C"\nx')
    row_generator = csv.get_table(csv_stream)
    next(row_generator)

def test_csv_error():
    csv_stream = BytesIO(b'"A";"B "bb" B";"C"\nx')
    row_generator = csv.get_table(csv_stream)
    with pytest.raises(SnutreeReaderError):
        next(row_generator)

def test_sql_mysql_error():
    with pytest.raises(SnutreeReaderError):
        sql.get_members_local('', {})

def test_sql_ssh_error():
    conf = {'host' : '', 'port' : 0, 'user' : '', 'private_key' : ''}
    with pytest.raises(SnutreeReaderError):
        sql.get_members_ssh('', conf, conf)

def test_dot_no_error():
    dot_stream = BytesIO(b'digraph { a -> b; }')
    dot.get_table(dot_stream)

def test_dot_error():
    dot_stream = BytesIO(b'digraph { \n a------ \n }')
    with pytest.raises(SnutreeReaderError):
        dot.get_table(dot_stream)

def test_json_no_error():
    json_stream = BytesIO(b'''[{"asdf": "fsdf"}, {"fsdf": "Asf"}]''')
    row_generator = json.get_table(json_stream)
    next(row_generator)

@pytest.mark.parametrize('document', [
    b'{"a": {"asdf": "fsdf"}, "b": {"fsdf": "Asf"}}', # top level isn't list
    b'[{asdf: "fsdf"}, {"fsdf": "Asf"}]', # not using double quotes
    b'[{"asdf": "fsdf"}, "asdf"]', # list contains non-dict elements
])
def test_json_error(document):
    json_stream = BytesIO(document)
    row_generator = json.get_table(json_stream)
    with pytest.raises(SnutreeReaderError):
        while True:
            next(row_generator)

