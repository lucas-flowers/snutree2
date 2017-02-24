import csv

def get_table(stream):
    '''
    Read a CSV from the stream and return a list of member dictionaries.
    '''
    return list(csv.DictReader(stream))



