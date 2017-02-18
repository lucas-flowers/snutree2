#!/usr/bin/env python
import subprocess, click, logging, sys, yaml, csv
from pathlib import Path
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
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', required=True, type=click.Path())
@click.option('--config', '-c', type=click.Path(exists=True), multiple=True)
@click.option('--seed', '-s', default=0)
@click.option('--verbose', '-v', is_flag=True, default=False)
@logged
def cli(paths, output, config, seed, verbose):
    '''
    Create a big-little family tree.
    '''

    if verbose:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s: %(message)s')

    logging.info('Retrieving big-little data from data sources')
    members = get_from_sources(paths)

    ###########################################################################
    ###########################################################################

    # Lines between the two comment rulers are the custom lines
    # TODO generalize this

    logging.info('Validating directory')
    directory = Directory(members, [Candidate, Brother, Knight, Expelled], ['Reaffiliate'])

    ###########################################################################
    ###########################################################################

    logging.info('Loading tree configuration')
    tree_cnf = load_configuration(config)

    logging.info('Constructing family tree data structure')
    tree = FamilyTree(directory, tree_cnf)

    logging.info('Creating internal DOT code representation')
    dotgraph = tree.to_dot_graph()

    logging.info('Converting DOT code representation to text')
    dotcode = dotgraph.to_dot()

    logging.info('Writing DOT file')
    dot_filename = output + '.dot'
    write_dotfile(dotcode, dot_filename)

    logging.info('Compiling DOT file to PDF with Graphviz')
    pdf_filename = output + '.pdf'
    write_pdffile(dotcode, pdf_filename)

def load_configuration(paths):
    config = {}
    for path in paths:
        with open(path, 'r') as f:
            config.update(yaml.safe_load(f))
    return config

def get_from_sources(paths):

    # TODO get better name
    table_getters = {
        '.yaml' : get_from_sql_settings,
        '.csv' : get_from_csv,
        }

    members = []
    for path in paths or []:
        filetype = Path(path).suffix
        table_getter = table_getters.get(filetype)
        if not table_getter:
            # TODO subclass NotImplementedError and catch it
            msg = 'Filetype "{}" not supported'
            raise NotImplementedError(msg.format(filetype))
        members += table_getter(path)

    return members

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


def get_from_csv(path):
    with open(path, 'r') as f:
        return list(csv.DictReader(f))

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

def get_from_sql_settings(path):
    with open(path, 'r') as f:
        return get_from_sql(yaml.safe_load(f))

def get_from_sql(cnf):
    '''
    Get the table of members from the SQL database.
    '''

    cnf = validate(MYSQL_CNF_VALIDATOR, cnf)
    return sql.get_table(cnf['query'], cnf['mysql'], ssh_cnf=cnf['ssh'])

if __name__ == '__main__':
    main()

