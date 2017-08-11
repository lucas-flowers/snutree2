from .. import SnutreeError

class SnutreeReaderError(SnutreeError):
    '''
    Use to wrap expected IO errors so that higher-level snutree functions can
    handle them instead of letting them raise all the way up.
    '''
    pass

