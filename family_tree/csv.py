import csv
from voluptuous import Schema, Optional
from voluptuous.humanize import validate_with_humanized_errors as validate
from family_tree.settings import read_settings
from family_tree.directory import Directory
from family_tree.semester import Semester

def retrieve_members(path):

    with open(path, 'r') as f:
        # Ignore reaffiliates
        rows = list(csv.DictReader(f))

    members = []
    for row in rows:

        validate(row, csv_member_validator)

        if row['status'] != 'Reaffiliate':

            semester = row['pledge_semester']
            if semester:
                row['pledge_semester'] = Semester(semester)

            if row['status'] in ('Active', 'Alumni', 'Left School'):
                row['status'] = 'Knight'

            # Delete all keys with null or empty values (fuck that noise)
            for key, field in list(row.items()):
                if not field:
                    del row[key]

            members.append(row)

    return members

# I don't trust a rando CSV file to have the right headers
csv_member_validator = Schema(dict(
    (fieldname, str) for fieldname in [
        'status',
        Optional('badge'),
        Optional('first_name'),
        Optional('preferred_name'),
        'last_name',
        'big_badge',
        'pledge_semester',
        ]), required=True)

def retrieve_affiliations(path):

    with open(path, 'r') as f:
        rows = list(csv.DictReader(f))

    affiliations = []
    for row in rows:

        validate(row, csv_affiliation_validator)

        badge = row['badge']
        other_badge = row['other_badge']
        chapter_name = row['chapter_name']

        if badge != other_badge or chapter_name != 'Delta Alpha':

            for key, field in list(row.items()):
                if not field:
                    del row[key]

            affiliations.append(row)

    return affiliations

csv_affiliation_validator = Schema(dict(
    (fieldname, str) for fieldname in [
    'badge',
    'chapter_name',
    'other_badge',
    ]), required=True)

# TODO move paths into settings
def to_directory(
        members_path,
        extra_members_path=None, # Intended for brothers not made knights
        affiliations_path=None,
        settings_path=None,
        ):

    directory = Directory()
    directory.set_members(retrieve_members(members_path) +
            (retrieve_members(extra_members_path) if extra_members_path else []))
    directory.affiliations = retrieve_affiliations(affiliations_path) if affiliations_path else []
    directory.settings = read_settings(settings_path) if settings_path else {}

    return directory


