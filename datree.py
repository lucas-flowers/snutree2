#!/usr/bin/env python
import subprocess, click, logging, sys, yaml
from snutree.readers import csv, sql
from snutree.schemas.sigmanu import Candidate, Brother, Knight, Expelled
from snutree.tree import FamilyTree, TreeError
from snutree.entity import TreeEntityAttributeError
from snutree.settings import retrieve_settings, SettingsError
from snutree.utilities import logged
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

@click.command()
@click.argument('settings_paths', nargs=-1, type=click.Path(exists=True))
@click.option('--name', required=True, type=click.Path())
@click.option('--civicrm', type=click.Path(exists=True))
@click.option('--seed', default=0)
@click.option('--debug/--no-debug', default=False)
@logged
def cli(settings_paths, name, civicrm, seed, debug):
    '''
    Create a big-little family tree.
    '''

    if debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s: %(message)s')

    logging.info('Reading configuration')
    settings = retrieve_settings(*settings_paths)

    logging.info('Retrieving big-little data from data source')
    if civicrm:
        with open(civicrm, 'r') as f:
            cnf = yaml.safe_load(f)
        members = get_from_civicrm(
                query, settings, cnf['mysql'], cnf['ssh']
                )
    elif settings.get('csv'):
        members = get_from_csv(
                settings['csv']['members']
                )
    else:
        raise Exception()

    logging.info('Validating directory')
    directory = to_directory(members)

    logging.info('Constructing family tree data structure')
    tree = FamilyTree(directory, settings)

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


query = "***REMOVED***"



def get_from_csv(path):

    return csv.get_table(path)

def get_from_civicrm(query, tree_cnf, mysql_cnf, ssh_cnf):
    '''
    Get the table of members from the SQL database. Adjust the values for
    compatibility with the Directory class.
    '''

    return sql.get_table(query, mysql_cnf, ssh_cnf=ssh_cnf)

def to_directory(member_list):
    '''
    Get the table of members from the SQL database. Adjust the values for
    compatibility with the Directory class.
    '''

    members = []
    for row in member_list:

        if row.get('status') != 'Reaffiliate':

            # Remove the keys pointing to falsy values from each member. This
            # simplifies code in the Directory class (e.g., Directory does not have
            # to worry about handling values of None or empty strings).
            for key, field in list(row.items()):
                if not field:
                    del row[key]

            members.append(row)

    return Directory(members, [Candidate, Brother, Knight, Expelled])

if __name__ == '__main__':
    main()

