import csv

def get_table(stream):
    '''
    Read a CSV from the stream and return a list of member dictionaries.
    '''
    rows = list(csv.DictReader(stream))
    for row in rows:
        # Remove the keys pointing to falsy values from each member. This
        # simplifies validation (e.g., we don't have to worry about
        # handling values of None or empty strings)
        for key, field in list(row.items()):
            if not field:
                del row[key]
        yield row

