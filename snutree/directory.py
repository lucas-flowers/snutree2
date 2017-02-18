from pprint import pformat
from collections import defaultdict
from cerberus import Validator
from .utilities import logged

# TODO remove this class?

class Directory:
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

        # Remove the keys pointing to falsy values from each member. This
        # simplifies code in the Directory class (e.g., Directory does not
        # have to worry about handling values of None or empty strings).
        members = []
        for row in member_list:
            for key, field in list(row.items()):
                if not field:
                    del row[key]
            members.append(row)

        self.member_schemas = {}
        for typ in member_types:
            for allowed in typ.schema['status']['allowed']:
                self.member_schemas[allowed] = typ.get_schema()

        self.ignored_statuses = set(ignored_statuses or ())

        self.set_members(members)

    @logged
    def set_members(self, members):

        member_status_map = defaultdict(list)
        for member in members:

            if len(self.member_schemas) == 1:
                # If there is only one type of member, ignore the status field
                # and fill it with that one type of member
                member['status'] = list(self.member_schemas.keys())[0]

            status = member.get('status')

            # Don't include if ignored
            if status in self.ignored_statuses:
                continue

            # Make sure the member status field is valid first
            if status not in self.member_schemas.keys():
                msg = 'Invalid member status in:\n{}\nStatus must be one of:\n{}'
                vals = pformat(member), list(self.member_schemas.keys())
                raise DirectoryError(msg.format(*vals))

            member_status_map[status].append(member)

        self._members = []
        for status, members in member_status_map.items():

            validator = Validator({'members' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'dict',
                    'schema' : self.member_schemas[status]['schema']
                    }
                }})

            if not validator.validate({'members' : members}):
                errors = []
                for member_errors in validator.errors['members']:
                    for i, error in member_errors.items():
                        errors.append({
                            'Invalid {}'.format(status) : validator.document['members'][i],
                            'Rules Violated' : error
                            })
                msg = 'Errors found in directory:\n{}'
                raise DirectoryError(msg.format(pformat(errors)))

            MemberType = self.member_schemas[status]['constructor']
            for member in validator.document['members']:
                self._members.append(MemberType(**member))

    def get_members(self):
        return self._members

class DirectoryError(Exception):
    pass

