import json, yaml
from family_tree import settings_schema

greek_mapping = {
        'Alpha' : 'A',
        'Beta' : 'B',
        'Gamma' : 'Γ',
        'Delta' : 'Δ',
        'Epsilon' : 'E',
        'Zeta' : 'Z',
        'Eta' : 'H',
        'Theta' : 'Θ',
        'Iota' : 'I',
        'Kappa' : 'K',
        'Lambda' : 'Λ',
        'Mu' : 'M',
        'Nu' : 'N',
        'Xi' : 'Ξ',
        'Omicron' : 'O',
        'Pi' : 'Π',
        'Rho' : 'P',
        'Sigma' : 'Σ',
        'Tau' : 'T',
        'Upsilon' : 'Y',
        'Phi' : 'Φ',
        'Chi' : 'X',
        'Psi' : 'Ψ',
        'Omega' : 'Ω',
        '(A)' : '(A)', # Because of Eta Mu (A) Chapter
        '(B)' : '(B)', # Because of Eta Mu (B) Chapter
        }

class TableReaderFunction:
    '''
    Each instance is a function that uses `read_row` to read each "row" in an
    iterable `table`. The function `read_row` should store each row in
    `container`, which is of type `container_type`.

    The instantiated function keeps track of the row number and provides the
    row number when an exception is raised. The starting row number defaults to
    1, but can be changed (i.e., for CSVs with headers).
    '''

    def __init__(self, read_row, container_type, first_row=1):
        self.read_row = read_row
        self.container_type = container_type
        self.first_row = first_row

    def __call__(self, table):

        container = self.container_type()
        row_number = self.first_row
        try:
            for row in table:
                self.read_row(row, container)
                row_number += 1
        except:
            # TODO use a real error
            raise Exception('Error in row {}'.format(row_number))

        return container

def to_greek_name(english_name):
    return ''.join([greek_mapping[w] for w in english_name.split(' ')])

def read_settings(path):
    with open(path, 'r') as f:

        # Load into YAML first, then dump into a JSON string, then load again
        # using the json library. This is done because YAML accepts nonstring
        # (i.e., integer) keys, but JSON and Graphviz do not. So if a key in
        # the settings file were an integer, the program's internal
        # representation could end up having two different versions of a node:
        # One with an integer key and another with a string key.
        #
        # This could easily be avoided by just not writing integers in the YAML
        # file, but that could be expecting too much of someone editing it.
        settings = json.loads(json.dumps(yaml.load(f)))

    settings_schema.validate(settings)
    return settings

