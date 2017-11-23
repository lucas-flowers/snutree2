import json
import io
from snutree.errors import SnutreeReaderError

def get_table(bytesio, **config):
    '''
    Read a JSON file from the stream and return a list of member dictionaries.
    '''

    textio = io.TextIOWrapper(bytesio, encoding='utf-8')

    try:
        rows = json.load(textio) or []
    except json.JSONDecodeError as e:
        msg = 'could not read json file:\n{e}'.format(e=e)
        raise SnutreeReaderError(msg)
    if not isinstance(rows, list):
        msg = 'input file must represent a list of dicts, not a {type}'.format(type=type(rows))
        raise SnutreeReaderError(msg)

    for row in rows:
        if not isinstance(row, dict):
            msg = 'input file must contain only dicts, not {type}'.format(type=type(row))
            raise SnutreeReaderError(msg)
        # Delete falsy values to simplify validation
        for key, field in list(row.items()):
            if not field:
                del row[key]
        yield row

