import MySQLdb, MySQLdb.cursors
from family_tree.settings import read_settings
from family_tree.csv import read_csv
from family_tree.directory import Directory


# TODO for SQL, make sure affiliations match up to the external ID.
# TODO sort affiliations





# TODO move paths into settings
def to_directory(
        settings_path,
        extra_members_path=None, # Intended for brothers not made knights
        ):

    settings = read_settings(settings_path)

    directory = Directory()
    directory.settings = settings

    mysql_cnf = settings['mysql']
    cxn = MySQLdb.Connection(**mysql_cnf)
    cursor = cxn.cursor(MySQLdb.cursors.DictCursor)

    # TODO Move to other function?
    cursor.execute(directory_query)
    directory.members = list(cursor.fetchall()) # fetchall returns a friggin tuple and this is the simplest solution if I want to append later

    for member in directory.members:

        # TODO make a simpler Semester call
        season = member['pledge_semester_season']
        year = member['pledge_semester_year']
        del member['pledge_semester_year']
        del member['pledge_semester_season']
        if season and year != None:
            member['pledge_semester'] = '{} {}'.format(season, year)
        else:
            member['pledge_semester'] = None

        member['badge'] = str(member['badge']) if member['badge'] else None
        member['big_badge'] = str(member['big_badge']) if member['big_badge'] else None

    directory.members += read_csv(extra_members_path) if extra_members_path else []


    cursor.execute(affiliations_query)
    raw_affiliations = cursor.fetchall()
    directory.affiliations = []

    for affiliation in raw_affiliations:

        # TODO Is this necessary? (it's doing two things: converting
        # badges from ints to strings (since keys should be strings), and
        # removing primary DA badges from the brother's list of affiliations,
        # to ensure there's no duplicate)
        badge = str(affiliation['badge'])
        other_badge = str(affiliation['other_badge'])
        if badge != other_badge or affiliation['chapter_name'] != 'Delta Alpha':
            directory.affiliations.append({
                'badge' : badge,
                'other_badge' : other_badge,
                'chapter_name' : affiliation['chapter_name'],
                })

    return directory

affiliations_query = "***REMOVED***"

directory_query = "***REMOVED***"

