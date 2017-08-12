from contextlib import closing
import MySQLdb
import MySQLdb.cursors
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
from cerberus import Validator
from . import SnutreeReaderError
from ..utilities.cerberus import validate, nonempty_string

# Validates a configuration YAML file with SQL and ssh options
SQL_CNF_VALIDATOR = Validator({

    'sql' : {

        'type' : 'dict',
        'required' : True,
        'schema' : {

            'host' : nonempty_string,
            'user' : nonempty_string,
            'passwd' : nonempty_string,
            'port' : { 'type': 'integer' },
            'db' : nonempty_string,

            # SSH for remote SQL databases
            'ssh' : {
                'type' : 'dict',
                'required' : False,
                'schema' : {
                    'host' : nonempty_string,
                    'port' : { 'type' : 'integer' },
                    'user' : nonempty_string,
                    'public_key' : nonempty_string,
                    }
                }

            },
        }
    }, allow_other=True)

def get_table(query_stream, **config):
    '''
    Read a YAML table with query, SQL and, optionally, ssh information. Use the
    information to get a list of member dictionaries.
    '''

    rows = get_members(query_stream.read(), config)
    for row in rows:
        # Remove the keys pointing to falsy values from each member. This
        # simplifies validation (e.g., we don't have to worry about
        # handling values of None or empty strings)
        for key, field in list(row.items()):
            if not field:
                del row[key]
        yield row

def get_members(query, config):
    '''
    Validate the configuration file and use it to get and return a table of
    members from the configuration's SQL database.
    '''

    config = validate(SQL_CNF_VALIDATOR, config)
    ssh_config = config['sql'].get('ssh')
    sql_config = config['sql'].copy()
    del sql_config['ssh']
    if ssh_config:
        return get_members_ssh(query, sql_config, ssh_config)
    else:
        return get_members_local(query, sql_config)

def get_members_local(query, sql_config):
    '''
    Use the query and SQL configuration to get a table of members.
    '''

    try:
        with closing(MySQLdb.Connection(**sql_config)) as cxn:
            with cxn.cursor(MySQLdb.cursors.DictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
    except MySQLdb.MySQLError as e:
        raise SnutreeReaderError(f'problem reading SQL database:\n{e}')

def get_members_ssh(query, sql, ssh):
    '''
    Use the query, SQL, and SSH configurations to get a table of members from
    a database through an SSH tunnel.
    '''

    options = {
            'ssh_address_or_host' : (ssh['host'], ssh['port']),
            'ssh_username' : ssh['user'],
            'ssh_pkey' : ssh['public_key'],
            'remote_bind_address' : (sql['host'], sql['port'])
            }

    try:

        with SSHTunnelForwarder(**options) as tunnel:
            tunneled_sql = sql.copy()
            tunneled_sql['port'] = tunnel.local_bind_port
            return get_members_local(query, tunneled_sql)

    # The sshtunnel module lets invalid assertions and value errors go
    # untouched, so catch them too
    except (BaseSSHTunnelForwarderError, AssertionError, ValueError) as e:
        raise SnutreeReaderError(f'problem connecting via SSH:\n{e}')

