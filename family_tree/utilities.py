
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

