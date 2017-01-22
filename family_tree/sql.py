import MySQLdb, MySQLdb.cursors
import family_tree.csv
from family_tree.settings import read_settings
from family_tree.directory import Directory
from family_tree.semester import Semester

# TODO for SQL, make sure DA affiliations agree with the external ID.
# TODO sort affiliations

# TODO move paths into settings
def to_directory(
        settings_path,
        extra_members_path=None, # Intended for brothers not made knights
        ):

    settings = read_settings(settings_path)
    mysql_cnf = settings['mysql']
    cxn = MySQLdb.Connection(**mysql_cnf)

    directory = Directory()
    directory.settings = settings
    directory.affiliations = retrieve_affiliations(cxn)
    # TODO you know, this `extra_members_path` could be the full local
    # directory, in addition to BNKs...
    directory.set_members(retrieve_members(cxn)
            + (family_tree.csv.retrieve_members(extra_members_path) if extra_members_path else [])
            )


    return directory

def retrieve_members(mysql_connection):

    cursor = mysql_connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(directory_query)
    members = list(cursor.fetchall()) # fetchall returns a friggin tuple and this is the simplest solution if I want to append later

    for member in members:

        # Delete all keys with null or empty values (fuck that noise)
        for key, field in list(member.items()):
            if not field:
                del member[key]

        # TODO make a simpler Semester call(?)
        # Convert pledge_semester to a Semester object
        season = member.pop('pledge_semester_season', None)
        year = member.pop('pledge_semester_year', None)
        if season and year != None:
            member['pledge_semester'] = Semester('{} {}'.format(season, year))

        # Collapse status categories that indicate types of Knights
        if member['status'] in ('Active', 'Alumni', 'Left School'):
            member['status'] = 'Knight'

    return members

def retrieve_affiliations(mysql_connection):

    cursor = mysql_connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(affiliations_query)

    # The fetchall() function returns a tuple, so we have to make the list from
    # scratch if we intend to remove elements.
    #
    # TODO do we need to remove elements now? (see TODO below). if we don't,
    # then the loop below can probably be removed
    raw_affiliations = cursor.fetchall()
    affiliations = []

    for aff in raw_affiliations:

        # TODO clean this mess up. it basically keeps only integer keys, since
        # DZs in the directory have "DZ____" as external IDs
        badge = str(aff['badge']) # TODO use integers instead
        try:
            int(badge)
        except:
            continue

        other_badge = str(aff['other_badge'])
        chapter_name = aff['chapter_name']
        aff = dict(badge=badge, other_badge=other_badge, chapter_name=chapter_name)

        # Delete all keys with null or empty values (fuck that noise)
        for key, field in list(aff.items()):
            if not field:
                del aff[key]

        # TODO is there a better way than looking for all primary DA badges and
        # removing them from the affiliations list?
        if badge != other_badge or chapter_name != 'Delta Alpha':
            affiliations.append(aff)

    return affiliations


###############################################################################
###############################################################################
#### Queries                                                               ####
###############################################################################
###############################################################################



affiliations_query = "***REMOVED***"

directory_query = "***REMOVED***"

