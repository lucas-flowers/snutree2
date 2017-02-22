from pprint import pformat
from .utilities import logged

@logged
def validate_members(member_list, member_types, ignored_statuses=None):

    ignored_statuses = ignored_statuses or []

    allowed_statuses = {}
    for typ in member_types:
        for allowed in typ.allowed:
            allowed_statuses[allowed] = typ

    members = []
    for member in member_list:

        # Remove the keys pointing to falsy values from each member. This
        # simplifies validation (e.g., we don't have to worry about
        # handling values of None or empty strings)
        for key, field in list(member.items()):
            if not field:
                del member[key]

        if len(allowed_statuses) == 1:
            # If there is only one type of member, ignore the status field
            #
            # TODO zero just takes the first one (it shouldn't matter, but
            # it's kind of ugly)
            status = next(iter(allowed_statuses.keys()))
        else:
            status = member.get('status')

        # Don't include if ignored
        if status in ignored_statuses:
            continue

        # Make sure the member status field is valid first
        if status not in allowed_statuses:
            msg = 'Invalid member status in:\n{}\nStatus must be one of:\n{}'
            vals = pformat(member), list(allowed_statuses.keys())
            raise DirectoryError(msg.format(*vals))

        # TODO error checking
        # TODO rename dict members and object members
        member = allowed_statuses[status].from_dict(member)
        members.append(member)

    return members

class DirectoryError(Exception):
    pass

