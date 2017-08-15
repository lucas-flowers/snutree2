import logging
import time
from functools import wraps

def logged(function):
    '''
    Sends timing information to the debug logger on functions this function
    decorates.
    '''

    logger = logging.getLogger(function.__module__)

    @wraps(function)
    def wrapped(*args, **kwargs):
        logger.debug('%s started . . .', function.__name__)
        t0 = time.time()
        result = function(*args, **kwargs)
        logger.debug('%s finished in ~%.2f ms', function.__name__, (time.time() - t0) * 1000 )
        return result

    return wrapped

