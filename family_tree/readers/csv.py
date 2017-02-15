import csv
from family_tree.directory import Directory
from family_tree.utilities import logged

def retrieve_directory(settings):

    members = retrieve_members(settings['csv']['members'])
    if settings.get('extra_members'):
        members += retrieve_members(settings['extra_members'])

    if settings['csv']['affiliations']:
        affiliations = retrieve_affiliations(settings['csv']['affiliations'])
    else:
        affiliations = {}

    return Directory(members, affiliations, settings)

@logged
def retrieve_members(path):
    '''
    Get the table of members from the CSV file at the given path. Adjust the
    table's values for compatibility with the Directory class.
    '''

    with open(path, 'r') as f:
        rows = list(csv.DictReader(f))

    members = []
    for row in rows:

        # The 'Reaffiliate' status is used to mark the extra badges for
        # brothers with more than one badge in the same chapter, so people
        # aren't confused when they find the same person twice. We don't need
        # this for the tree, so ignore all reaffiliate badges.
        if row.get('status') != 'Reaffiliate':

            # Remove keys pointing to falsy values for each member.
            for key, field in list(row.items()):
                if not field:
                    del row[key]

            # Collapse status categories that indicate types of Knights
            if row.get('status') in ('Active', 'Alumni', 'Left School'):
                row['status'] = 'Knight'

            members.append(row)

    return members

@logged
def retrieve_affiliations(path):
    '''
    Get the table of affiliations from the CSV file at the given path. Adjust
    the table's values for compatibility with the Directory class.
    '''

    with open(path, 'r') as f:
        rows = list(csv.DictReader(f))

    affiliations = []
    for row in rows:

        badge = row.get('badge')
        other_badge = row.get('other_badge')
        chapter_name = row.get('chapter_name')

        # Primary Delta Alpha badges are already handled separately; don't
        # include the duplicates.
        if not (chapter_name == 'Delta Alpha' and badge == other_badge and badge):

            # Delete all keys pointing to falsy values
            for key, field in list(row.items()):
                if not field:
                    del row[key]

            affiliations.append(row)

    return affiliations

