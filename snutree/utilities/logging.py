import sys
import logging
import time
import inspect
from functools import wraps
from ..errors import SnutreeError

def setup_logger(verbose, debug, quiet, log_path=None):
    '''
    Creates a top-level logger for the snutree package called 'snutree',
    intended for use in the snutree.cli and snutree.qt modules. Also creates
    two handlers:

    #. Standard error: Writes warnings and errors to stderr by default. The
    verbose flag will add INFO, and the debug flag will add DEBUG. The quiet
    flag will suppress warnings and include only errors.

    #. Log file: Writes all events at the INFO level of severity. The verbose
    and quiet flags have no effect, but the debug flag will add DEBUG events to
    the log. If no log_path is provided, there will be no log file.
    '''

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

    # Standard error handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(level if not quiet else logging.ERROR)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # File handler
    if log_path:
        try:
            file_handler = logging.FileHandler(log_path)
        except IOError as e:
            msg = 'could not open log file:\n{e}'.format(e=e)
            raise SnutreeError(msg)
        file_handler.setLevel(min(logging.INFO, level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def logged(function):
    '''
    Wraps around a function, logging the amount of time it takes to run that
    function every time it is called.
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

