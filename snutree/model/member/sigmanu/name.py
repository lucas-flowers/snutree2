import difflib
from typing import Optional


def get_full_preferred_name(
    first_name: str,
    preferred_name: Optional[str],
    last_name: str,
    threshold: float = 0.5,
) -> str:
    """
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
    """

    if not preferred_name or preferred_name == first_name:
        # ratio() is expensive, so first make sure the preferred name exists
        # and it isn't actually equal to the first name
        pass
    elif difflib.SequenceMatcher(None, preferred_name, last_name).ratio() < threshold:
        # preferred and last names are not too similar
        first_name = preferred_name
    else:
        # preferred and last names are too similar
        pass

    return f"{first_name} {last_name}"
