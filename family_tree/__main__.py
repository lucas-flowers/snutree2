import os, subprocess, click, logging, sys
from family_tree.tree import FamilyTree, TreeError
from family_tree.entity import TreeEntityError
from family_tree.settings import retrieve_settings, SettingsError
from family_tree.utilities import logged
from family_tree.directory import DirectoryError
from family_tree import csv, sql, dotread

@click.command()
@click.argument('settings_path')
@click.option('--seed', default=0)
@logged
def main(settings_path, seed):
    '''
    Create a big-little family tree.
    '''

    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s %(levelname)s: %(name)s - %(message)s')
    logging.info('Started')

    settings = retrieve_settings(settings_path)
    settings['seed'] = seed or settings.get('seed')

    if settings.get('mysql'):
        directory = sql
    elif settings.get('csv'):
        directory = csv
    else: # 'dot' in settings
        directory = dotread

    directory = directory.retrieve_directory(settings)
    tree = FamilyTree(directory)
    dotgraph = tree.to_dot_graph()
    dotcode = dotgraph.to_dot()

    folder = settings['output']['folder']

    dot_filename = os.path.join(folder, settings['output']['name'] + '.dot')
    write_dotfile(dotcode, dot_filename)

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
    except (TreeError, TreeEntityError, DirectoryError, SettingsError) as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error('Unexpected error.', exc_info=True)
        sys.exit(1)


