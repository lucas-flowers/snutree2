import os, subprocess, click, logging
from family_tree.tree import FamilyTree
from family_tree.settings import retrieve_settings
from family_tree.utilities import logged
from family_tree import csv, sql, dotread

@click.command()
@click.argument('settings_path')
def main(settings_path):
    '''
    Create a big-little family tree.
    '''

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info('Started')

    settings = retrieve_settings(settings_path)

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

    main()

