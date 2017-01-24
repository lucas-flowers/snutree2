import csv
from voluptuous import Schema, Optional
from voluptuous.humanize import validate_with_humanized_errors as validate
from family_tree.directory import Directory

# Required headers in a CSV members file
csv_member_schema = Schema({
    'status' : str,
    Optional('badge') : str,
    Optional('first_name') : str,
    Optional('preferred_name') : str,
    'last_name' : str,
    'big_badge' : str,
    'pledge_semester' : str,
    }, required=True)

# Required headers in a CSV affiliations file
csv_affiliation_schema = Schema({
    'badge' : str,
    'chapter_name' : str,
    'other_badge' : str,
    }, required=True)

def retrieve_directory(settings):

    members = retrieve_members(settings['file']['members'])
    if 'extra_members' in settings:
        members += retrieve_members(settings['extra_members'])

    affiliations = retrieve_affiliations(settings['file']['affiliations'])

    return Directory(members, affiliations, settings)

def retrieve_members(path):
    '''
    Get the table of members from the CSV file at the given path. Adjust the
    table's values for compatibility with the Directory class.
    '''

    with open(path, 'r') as f:
        rows = list(csv.DictReader(f))

    members = []
    for row in rows:

        # Make sure all required fields exist
        validate(row, csv_member_schema)

        # The 'Reaffiliate' status is used to mark the extra badges for
        # brothers with more than one badge in the same chapter, so people
        # aren't confused when they find the same person twice. We don't need
        # this for the tree, so ignore all reaffiliate badges.
        if row['status'] != 'Reaffiliate':

            # Remove keys point to falsy values for each member.
            for key, field in list(row.items()):
                if not field:
                    del row[key]

            # Collapse status categories that indicate types of Knights
            if row.get('status', None) in ('Active', 'Alumni', 'Left School'):
                row['status'] = 'Knight'

            members.append(row)

    return members

def retrieve_affiliations(path):
    '''
    Get the table of affiliations from the CSV file at the given path. Adjust
    the table's values for compatibility with the Directory class.
    '''

    with open(path, 'r') as f:
        rows = list(csv.DictReader(f))

    affiliations = []
    for row in rows:

        # Make sure all required fields exist
        validate(row, csv_affiliation_schema)

        badge = row['badge']
        other_badge = row['other_badge']
        chapter_name = row['chapter_name']

        # Primary Delta Alpha badges are already handled separately; don't
        # include the duplicates.
        if not (chapter_name == 'Delta Alpha' and badge == other_badge):

            # Delte all keys pointing to falsy values
            for key, field in list(row.items()):
                if not field:
                    del row[key]

            affiliations.append(row)

    return affiliations

