import os, subprocess, click, logging, sys
from family_tree.tree import FamilyTree, TreeError
from family_tree.entity import TreeEntityAttributeError
from family_tree.settings import retrieve_settings, SettingsError
from family_tree.utilities import logged
from family_tree.directory import DirectoryError
from family_tree import csv, sql, dotread

@click.command()
@click.argument('settings_paths', nargs=-1, type=click.Path(exists=True))
@click.option('--seed', default=0)
@click.option('--debug/--no-debug', default=False)
@logged
def main(settings_paths, seed, debug):
    '''
    Create a big-little family tree.
    '''

    if debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s: %(message)s')

    logging.info('Reading configuration')
    settings = retrieve_settings(*settings_paths)
    settings['seed'] = seed or settings.get('seed')
    logging.info('Using seed=%s', settings['seed'])

    if settings.get('mysql'):
        directory = sql
    elif settings.get('csv'):
        directory = csv
    else: # 'dot' in settings
        directory = dotread

    logging.info('Retrieving big-little data from data source')
    directory = directory.retrieve_directory(settings)

    logging.info('Constructing family tree data structure')
    tree = FamilyTree(directory)

    logging.info('Creating internal DOT code representation')
    dotgraph = tree.to_dot_graph()

    logging.info('Converting DOT code representation to text')
    dotcode = dotgraph.to_dot()

    folder = settings['output']['folder']

    logging.info('Writing DOT file')
    dot_filename = os.path.join(folder, settings['output']['name'] + '.dot')
    write_dotfile(dotcode, dot_filename)

    logging.info('Compiling DOT file to PDF with Graphviz')
    pdf_filename = os.path.join(folder, settings['output']['name'] + '.pdf')
    write_pdffile(dotcode, pdf_filename)

@logged
def write_dotfile(dotcode, filename):
    with open(filename, 'w+') as dotfile:
        dotfile.write(dotcode)

@logged
def write_pdffile(dotcode, pdf_filename):
    subprocess.run(['dot', '-Tpdf', '-o', pdf_filename],
            check=True, input=dotcode, universal_newlines=True)

if __name__ == '__main__':

    try:
        main()
    except (TreeError, TreeEntityAttributeError, DirectoryError, SettingsError) as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error('Unexpected error.', exc_info=True)
        sys.exit(1)


