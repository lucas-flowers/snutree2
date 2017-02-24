import logging, time
from .. import SnutreeError

class SettingsError(SnutreeError):
    pass

def logged(function):

    logger = logging.getLogger(function.__module__)

    def wrapped(*args, **kwargs):
        logger.debug('%s started . . .', function.__name__)
        t0 = time.time()
        result = function(*args, **kwargs)
        logger.debug('%s finished in ~%.2f ms', function.__name__, (time.time() - t0) * 1000 )
        return result

    return wrapped

