from abc import ABCMeta
from pprint import pformat
from .utilities import logged

# TODO remove this class?

class Directory(metaclass=ABCMeta):
    '''
    This class is used to store data from either a CSV file or a SQL query. It
    is an intermediate form before the data is turned into a tree. It stores a
    list of brothers from the directory.

    The Directory class guarantees that entries in its members and affiliations
    lists will be dictionaries that follow the following schema. Furthermore,
    the class guarantees that all chapter_name/other_badge pairs in the
    affiliations are unique.
    '''

    def __init__(self, member_list, member_types, ignored_statuses=None):

        self.ignored_statuses = ignored_statuses or []

        self.allowed_statuses = {}
        for typ in member_types:
            for allowed in typ.allowed:
                self.allowed_statuses[allowed] = typ

        self.set_members(member_list)

    @logged
    def set_members(self, members):

        self._members = []
        for member in members:

            # Remove the keys pointing to falsy values from each member. This
            # simplifies validation (e.g., we don't have to worry about
            # handling values of None or empty strings)
            for key, field in list(member.items()):
                if not field:
                    del member[key]

            if len(self.allowed_statuses) == 1:
                # If there is only one type of member, ignore the status field
                #
                # TODO zero just takes the first one (it shouldn't matter, but
                # it's kind of ugly)
                status = next(iter(self.allowed_statuses.keys()))
            else:
                status = member.get('status')

            # Don't include if ignored
            if status in self.ignored_statuses:
                continue

            # Make sure the member status field is valid first
            if status not in self.allowed_statuses:
                msg = 'Invalid member status in:\n{}\nStatus must be one of:\n{}'
                vals = pformat(member), list(self.allowed_statuses.keys())
                raise DirectoryError(msg.format(*vals))

            # TODO error checking
            self._members.append(self.allowed_statuses[status].from_dict((member)))

    def get_members(self):
        return self._members

class DirectoryError(Exception):
    pass

