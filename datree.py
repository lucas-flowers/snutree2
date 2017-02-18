#!/usr/bin/env python
import subprocess, click, logging, sys, yaml, csv
from cerberus import Validator
from snutree.readers import sql
from snutree.schemas.sigmanu import Candidate, Brother, Knight, Expelled
from snutree.tree import FamilyTree, TreeError
from snutree.entity import TreeEntityAttributeError
from snutree.utilities import logged, SettingsError, nonempty_string, validate
from snutree.directory import Directory, DirectoryError

def main():

    try:
        cli()
    except (TreeError, TreeEntityAttributeError, DirectoryError, SettingsError) as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error('Unexpected error.', exc_info=True)
        sys.exit(1)

# TODO shorten option names
@click.command()
@click.argument('tables', nargs=-1, type=click.Path(exists=True))
@click.option('--name', required=True, type=click.Path())
@click.option('--settings', type=click.Path(exists=True))
@click.option('--civicrm', type=click.Path(exists=True))
@click.option('--seed', default=0)
@click.option('--debug/--no-debug', default=False)
@logged
def cli(tables, settings, name, civicrm, seed, debug):
    '''
    Create a big-little family tree.
    '''

    if debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s: %(message)s')

    ###########################################################################
    ###########################################################################

    # Lines between the two comment rulers are the custom lines
    # TODO generalize this

    logging.info('Retrieving big-little data from data source')
    members = []
    for table in tables or []:
        members += get_from_csv(table)
    if civicrm:
        members += get_from_civicrm_settings(civicrm)

    logging.info('Validating directory')
    directory = Directory(members, [Candidate, Brother, Knight, Expelled], ['Reaffiliate'])

    ###########################################################################
    ###########################################################################

    logging.info('Constructing family tree data structure')
    with open(settings, 'r') as f:
        tree_cnf = yaml.safe_load(f)
    tree = FamilyTree(directory, tree_cnf)

    logging.info('Creating internal DOT code representation')
    dotgraph = tree.to_dot_graph()

    logging.info('Converting DOT code representation to text')
    dotcode = dotgraph.to_dot()

    logging.info('Writing DOT file')
    dot_filename = name + '.dot'
    write_dotfile(dotcode, dot_filename)

    logging.info('Compiling DOT file to PDF with Graphviz')
    pdf_filename = name + '.pdf'
    write_pdffile(dotcode, pdf_filename)

@logged
def write_dotfile(dotcode, filename):
    with open(filename, 'w+') as dotfile:
        dotfile.write(dotcode)

@logged
def write_pdffile(dotcode, pdf_filename):
    subprocess.run(['dot', '-Tpdf', '-o', pdf_filename],
            check=True, input=dotcode, universal_newlines=True)

# TODO for SQL, make sure DA affiliations agree with the external ID.
# TODO sort affiliations in each member


QUERY = "***REMOVED***"



def get_from_csv(path):
    with open(path, 'r') as f:
        return list(csv.DictReader(f))

MYSQL_CNF_VALIDATOR = Validator({

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

def get_from_civicrm_settings(path):
    with open(path, 'r') as f:
        return get_from_civicrm(yaml.safe_load(f))

def get_from_civicrm(cnf):
    '''
    Get the table of members from the SQL database.
    '''

    cnf = validate(MYSQL_CNF_VALIDATOR, cnf)
    return sql.get_table(QUERY, cnf['mysql'], ssh_cnf=cnf['ssh'])

if __name__ == '__main__':
    main()

