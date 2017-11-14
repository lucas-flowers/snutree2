import csv
import io
from snutree.errors import SnutreeReaderError

CONFIG_SCHEMA = {} # No configuration

def get_table(bytesio, **config):
    '''
    Read a CSV from the stream and return a list of member dictionaries.
    '''

    textio = io.TextIOWrapper(bytesio, encoding='utf-8')

    try:
        rows = list(csv.DictReader(textio, strict=True))
    except csv.Error as e:
        msg = 'could not read csv:\n{e}'.format(e=e)
        raise SnutreeReaderError(msg)

    for row in rows:
        # Delete falsy values to simplify validation
        for key, field in list(row.items()):
            if not field:
                del row[key]
        yield row

