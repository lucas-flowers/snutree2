
import difflib

def preferred(first_name, preferred_name, last_name, threshold=.5):
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

    return '{first_name} {last_name}'.format(first_name=first_name, last_name=last_name)

