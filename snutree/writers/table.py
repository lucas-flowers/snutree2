
'''
Special writing module for skipping tree generation.
'''

import sys
from io import StringIO
from csv import DictWriter

filetypes = {
        'csv',
        }

def compile_tree(tree, RankType, config):
    msg = 'The table module is a special built-in writer that does not write trees.'
    raise NotImplementedError(msg)

def compile_table(table):
    '''
    Returns the bytes of a raw table from the readers.
    '''

    # The following is definitely inefficient

    # Find all the headers
    fieldnames = {}
    for row in table:
        fieldnames |= row.keys()

    output = StringIO()
    writer = DictWriter(output, fieldnames)
    writer.writeheader()
    for row in table:
        writer.writerow(row)

    return bytes(output.getvalue(), encoding=sys.getdefaultencoding())

