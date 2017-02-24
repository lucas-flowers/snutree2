import logging, time, difflib

def logged(function):
    '''
    Sends timing information to the debug logger on functions this function
    decorates.
    '''

    logger = logging.getLogger(function.__module__)

    def wrapped(*args, **kwargs):
        logger.debug('%s started . . .', function.__name__)
        t0 = time.time()
        result = function(*args, **kwargs)
        logger.debug('%s finished in ~%.2f ms', function.__name__, (time.time() - t0) * 1000 )
        return result

    return wrapped

def combine_names(first_name, preferred_name, last_name, threshold=.5):
    '''
    This function returns:

        EITHER: "<preferred> <last>" if the preferred name is not too similar
        to the last name, depending on the threshold

        OR: "<first> <last>" if the preferred and last names are too similar

    This might provide a marginally incorrect name for those who

        a. go by something other than their first name that
        b. is similar to their last name,

    but otherwise it should almost always[^note] provide something reasonable.

    The whole point here is to

        a. avoid using *only* last names on the tree, while
        b. using the "first" names brothers actually go by, and while
        c. avoiding using a first name that is a variant of the last name.

    [^note]: I say "almost always" because, for example, someone with the
    last name "Richards" who goes by "Dick" will be listed incorrectly as "Dick
    Richards" even if his other names are neither Dick nor Richard (unless the
    tolerance threshold is made very low).
    '''

    # ratio() is expensive, so first make sure the strings aren't actually equal
    if not preferred_name or preferred_name == first_name:
        pass
    elif difflib.SequenceMatcher(None, preferred_name, last_name).ratio() < threshold:
        first_name = preferred_name

    return '{} {}'.format(first_name, last_name)

