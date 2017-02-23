import MySQLdb, MySQLdb.cursors
from contextlib import closing
from sshtunnel import SSHTunnelForwarder
from cerberus import Validator
from ..utilities import validate, nonempty_string

MYSQL_CNF_VALIDATOR = Validator({

    'query' : nonempty_string,

    'mysql' : {
        'type' : 'dict',
        'required' : True,
        'schema' : {
            'host' : nonempty_string,
            'user' : nonempty_string,
            'passwd' : nonempty_string,
            'port' : { 'type': 'integer' },
            'db' : nonempty_string,
            }
        },

    # SSH for remote MySQL databases
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

    })

def get_table(query, mysql_cnf, ssh_cnf=None):

    if not ssh_cnf:
        return get_table_no_tunnel(query, mysql_cnf)

    options = {
            'ssh_address_or_host' : (ssh_cnf['host'], ssh_cnf['port']),
            'ssh_username' : ssh_cnf['user'],
            'ssh_pkey' : ssh_cnf['public_key'],
            'remote_bind_address' : (mysql_cnf['host'], mysql_cnf['port'])
            }

    with SSHTunnelForwarder(**options) as tunnel:
        tunneled_mysql_cnf = mysql_cnf.copy()
        tunneled_mysql_cnf['port'] = tunnel.local_bind_port
        return get_table_no_tunnel(query, tunneled_mysql_cnf)

def get_table_from_cnf(cnf):
    '''
    Get the table of members from the SQL database.
    '''

    cnf = validate(MYSQL_CNF_VALIDATOR, cnf)
    return get_table(cnf['query'], cnf['mysql'], ssh_cnf=cnf['ssh'])

def get_table_no_tunnel(query, mysql_cnf):

    with closing(MySQLdb.Connection(**mysql_cnf)) as cxn:
        with cxn.cursor(MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

