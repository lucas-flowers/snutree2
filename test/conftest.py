
from inspect import cleandoc

def trim(string):
    '''
    Remove all leading whitespace, common indentation, and trailing whitespace
    (except for the final, standard newline).
    '''
    return cleandoc(string) + '\n'

