
class SnutreeError(Exception):
    pass

class SnutreeReaderError(SnutreeError):
    '''
    Problems with reading input files.
    '''
    pass

class SnutreeWriterError(SnutreeError):
    '''
    Problems with creating output files.
    '''
    pass

class SnutreeSchemaError(SnutreeError):
    '''
    Problems when attempting to convert a table row into a Member. Allows the
    offending row to be displayed alongside the error message.
    '''

    def __init__(self, error, data):
        '''
        Store the original validation error along with the data that caused.
        '''
        self.error = error
        self.data = data

    def __str__(self):
        return '{error}. In:\n{data}'.format(error=self.error, data=self.data)

