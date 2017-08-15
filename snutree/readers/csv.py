import csv
from snutree.errors import SnutreeReaderError

def get_table(stream, **config):
    '''
    Read a CSV from the stream and return a list of member dictionaries.
    '''

    try:
        rows = list(csv.DictReader(stream, strict=True))
    except csv.Error as e:
        raise SnutreeReaderError(f'could not read csv:\n{e}')

    for row in rows:
        # Delete falsy values to simplify validation
        for key, field in list(row.items()):
            if not field:
                del row[key]
        yield row

