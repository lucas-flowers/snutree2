import csv

def get_table(path):
    with open(path, 'r') as f:
        return list(csv.DictReader(f))

