import MySQLdb, MySQLdb.cursors
from sshtunnel import SSHTunnelForwarder as forwarder
from . import csv
from ..entity import Candidate, Brother, Knight, Expelled
from ..directory import Directory
from ..utilities import logged

# TODO for SQL, make sure DA affiliations agree with the external ID.
# TODO sort affiliations in each member

# Query of affiliations in CiviCRM directory
affiliations_query = "***REMOVED***"

# Query of members and big/littles in CiviCRM directory
directory_query = "***REMOVED***"

def sshtunnel(fn):

    def fn_wrapped(settings):

        ssh = settings.get('ssh', None)
        if not ssh:
            return fn(settings)

        mysql = settings['mysql']
        remote = ssh['host'], ssh['port']
        user = ssh['user']
        key = ssh['public_key']
        remote_bind = mysql['host'], mysql['port']

        with forwarder(remote,
                ssh_username=user,
                ssh_pkey=key,
                remote_bind_address=remote_bind) as tunnel:
            mysql['port'] = tunnel.local_bind_port
            return fn(settings)

    return fn_wrapped

@sshtunnel
def retrieve_directory(settings):

    mysql_cnf = settings['mysql']
    cxn = MySQLdb.Connection(**mysql_cnf)

    members = retrieve_members(cxn)
    if settings.get('extra_members'):
        members += csv.retrieve_members(settings['extra_members'])

    affiliations = retrieve_affiliations(cxn)

    return Directory(members, affiliations, settings,
            [Candidate, Brother, Knight, Expelled])

@logged
def retrieve_members(mysql_connection):
    '''
    Get the table of members from the SQL database. Adjust the values for
    compatibility with the Directory class.
    '''

    cursor = mysql_connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(directory_query)
    rows = cursor.fetchall()

    members = []
    for row in rows:

        # Remove the keys pointing to falsy values from each member. This
        # simplifies code in the Directory class (e.g., Directory does not have
        # to worry about handling values of None or empty strings).
        for key, field in list(row.items()):
            if not field:
                del row[key]

        # Combine the season and year into one string
        season = row.pop('pledge_semester_season', None)
        year = row.pop('pledge_semester_year', None)
        if season and year != None:
            row['pledge_semester'] = ' '.join((season, str(year)))

        # Collapse status categories that indicate types of Knights
        if row.get('status', None) in ('Active', 'Alumni', 'Left School'):
            row['status'] = 'Knight'

        members.append(row)

    return members

def retrieve_affiliations(mysql_connection):
    '''
    Get the table of affiliations from the SQL database. Adjust the values for
    compatibility with the Directory class.
    '''

    cursor = mysql_connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(affiliations_query)
    rows = cursor.fetchall()

    affiliations = []
    for row in rows:

        badge = str(row['badge'])
        other_badge = str(row['other_badge'])
        chapter_name = row['chapter_name']

        # The Delta Alpha badges used as external IDs in CiviCRM are already
        # handled separately; don't include the duplicates.
        if not (chapter_name == 'Delta Alpha' and badge == other_badge):

            # Update row with the new values set above
            row.update(dict(badge=badge, other_badge=other_badge, chapter_name=chapter_name))

            # Delete all keys pointing to falsy values
            for key, field in list(row.items()):
                if not field:
                    del row[key]

            affiliations.append(row)

    return affiliations

