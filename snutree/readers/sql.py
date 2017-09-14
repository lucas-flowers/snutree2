from contextlib import closing
from snutree.errors import SnutreeReaderError
from snutree.utilities.cerberus import Validator

CONFIG_SCHEMA = {

        'host' : {
            'description' : 'SQL server hostname',
            'type' : 'string',
            'default' : '127.0.0.1'
            },
        'user' : {
            'description' : 'SQL username',
            'type' : 'string',
            'default' : 'root'
            },
        'passwd' : {
            'description' : 'SQL user password',
            'type' : 'string',
            },
        'port' : {
            'description' : 'SQL server port',
            'type': 'integer',
            'default' : 3306
            },
        'db' : {
            'description' : 'SQL database name',
            'type' : 'string',
            },

        # SSH for remote SQL databases
        'ssh' : {
            'description' : 'credentials to encrypt SQL connection with SSH',
            'type' : 'dict',
            'required' : False,
            'nullable' : True,
            'schema' : {
                'host' : {
                    'description' : 'SSH server hostname',
                    'type' : 'string',
                    },
                'port' : {
                    'description' : 'SSH server port',
                    'type' : 'integer',
                    'default' : 22
                    },
                'user' : {
                    'description' : 'SSH username',
                    'type' : 'string',
                    },
                'private_key' : {
                    'description' : 'SSH private keyfile path',
                    'type' : 'string',
                    },
                }
            }
        }

# Validates a configuration YAML file with SQL and ssh options
CONFIG_VALIDATOR = Validator(CONFIG_SCHEMA)

def get_table(query_stream, **config):
    '''
    Read a YAML table with query, SQL and, optionally, ssh information. Use the
    information to get a list of member dictionaries.
    '''

    rows = get_members(query_stream.read(), config)
    for row in rows:
        # Delete falsy values to simplify validation
        for key, field in list(row.items()):
            if not field:
                del row[key]
        yield row

def get_members(query, config):
    '''
    Validate the configuration file and use it to get and return a table of
    members from the configuration's SQL database.
    '''

    config = CONFIG_VALIDATOR.validated(config)
    ssh_config = config.get('ssh')
    sql_config = config.copy()
    sql_config.pop('ssh', None)
    if ssh_config:
        return get_members_ssh(query, sql_config, ssh_config)
    else:
        return get_members_local(query, sql_config)

def get_members_local(query, sql_config):
    '''
    Use the query and SQL configuration to get a table of members.
    '''

    try:
        import MySQLdb
    except ImportError: # 3.6: ModuleNotFoundError:
        msg = 'could not read SQL database: missing MySQLdb package'
        raise SnutreeReaderError(msg)

    import MySQLdb.cursors

    try:
        with closing(MySQLdb.Connection(**sql_config)) as cxn:
            with cxn.cursor(MySQLdb.cursors.DictCursor) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
    except MySQLdb.MySQLError as e:
        msg = 'problem reading SQL database:\n{e}'.format(e=e)
        raise SnutreeReaderError(msg)

def get_members_ssh(query, sql, ssh):
    '''
    Use the query, SQL, and SSH configurations to get a table of members from
    a database through an SSH tunnel.
    '''

    options = {
            'ssh_address_or_host' : (ssh['host'], ssh['port']),
            'ssh_username' : ssh['user'],
            'ssh_pkey' : ssh['private_key'],
            'remote_bind_address' : (sql['host'], sql['port'])
            }

    try:
        from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
    except ImportError: # 3.6: ModuleNotFoundError:
        msg = 'could not connect to SQL server via ssh: missing sshtunnel package'
        raise SnutreeReaderError(msg)

    try:

        with SSHTunnelForwarder(**options) as tunnel:
            tunneled_sql = sql.copy()
            tunneled_sql['port'] = tunnel.local_bind_port
            return get_members_local(query, tunneled_sql)

    # The sshtunnel module lets invalid assertions and value errors go
    # untouched, so catch them too
    except (BaseSSHTunnelForwarderError, AssertionError, ValueError) as e:
        msg = 'problem connecting via ssh:\n{e}'.format(e=e)
        raise SnutreeReaderError(msg)

