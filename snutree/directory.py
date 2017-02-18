from pprint import pformat
from collections import defaultdict
from cerberus import Validator
from .utilities import logged

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

    def __init__(self, member_list, member_types):

        self.member_schemas = {}
        for typ in member_types:
            for allowed in typ.schema['status']['allowed']:
                self.member_schemas[allowed] = typ.get_schema()

        self.set_members(member_list)

    @logged
    def set_members(self, members):

        member_status_map = defaultdict(list)
        for member in members:

            # Make sure the member status field is valid first
            if member.get('status') not in self.member_schemas.keys():
                msg = 'Invalid member status in:\n{}\nStatus must be one of:\n{}'
                vals = pformat(member), list(self.member_schemas.keys())
                raise DirectoryError(msg.format(*vals))

            member_status_map[member['status']].append(member)

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

