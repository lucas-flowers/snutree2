import MySQLdb, MySQLdb.cursors
from family_tree.settings import read_settings
from family_tree.csv import read_csv
from family_tree.directory import Directory

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
    directory.members = retrieve_members(cxn)
    # TODO you know, this `extra_members_path` could be the full local
    # directory, in addition to BNKs...
    directory.members += read_csv(extra_members_path) if extra_members_path else []

    return directory

def retrieve_members(mysql_connection):

    cursor = mysql_connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(directory_query)
    members = list(cursor.fetchall()) # fetchall returns a friggin tuple and this is the simplest solution if I want to append later

    for member in members:

        # TODO make a simpler Semester call(?)
        season = member.pop('pledge_semester_season')
        year = member.pop('pledge_semester_year')
        member['pledge_semester'] = '{} {}'.format(season, year) \
                if season and year != None else None

        member['badge'] = str(member['badge']) if member['badge'] else None
        member['big_badge'] = str(member['big_badge']) if member['big_badge'] else None

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

        # TODO the string conversion is necessary, right?
        badge = str(aff['badge'])
        other_badge = str(aff['other_badge'])
        chapter_name = aff['chapter_name']

        # TODO is there a better way than looking for all primary DA badges and
        # removing them from the affiliations list?
        if badge != other_badge or chapter_name != 'Delta Alpha':
            affiliations.append({
                'badge' : badge,
                'other_badge' : other_badge,
                'chapter_name' : chapter_name,
                })

    return affiliations


affiliations_query = "***REMOVED***"

directory_query = "***REMOVED***"

