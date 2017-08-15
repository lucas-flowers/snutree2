import sys
import logging
import time
import inspect
from functools import wraps
from .errors import SnutreeError

def create_snutree_logger(verbose, debug, quiet, log_path=None):

    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Use a more detailed log format for debugging
    if level <= logging.DEBUG:
        fmt = '%(asctime)s %(levelname)5s: %(name)s - %(message)s'
    else:
        fmt = '%(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt)

    logger = logging.getLogger('snutree')
    logger.setLevel(min(logging.INFO, level))

    # Standard error handler: Log records according to the level given in the
    # arguments.
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(level if not quiet else logging.ERROR)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # File handler: If a log file is provided, logs at a level of detail of at
    # least INFO and maybe more depending the arguments.
    if log_path:
        try:
            file_handler = logging.FileHandler(log_path)
        except IOError as e:
            msg = f'could not open log file:\n{e}'
            raise SnutreeError(msg)
        file_handler.setLevel(min(logging.INFO, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def logged(function):
    '''
    Sends timing information to the debug logger on functions this function
    decorates.
    '''

    logger = logging.getLogger(inspect.getmodule(function).__name__)

    @wraps(function)
    def wrapped(*args, **kwargs):
        logger.debug('%s started . . .', function.__name__)
        start_time = time.time()
        result = function(*args, **kwargs)
        logger.debug('%s finished in ~%.2f ms', function.__name__, (time.time() - start_time) * 1000 )
        return result

    return wrapped

