import os, subprocess, click
from family_tree.tree import FamilyTree
from family_tree.settings import retrieve_settings
from family_tree import csv, sql, dotread

@click.command()
@click.argument('settings_path')
def main(settings_path):
    '''
    Create a big-little family tree.
    '''

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
    with open(dot_filename, 'w+') as dotfile:
        dotfile.write(dotcode)

    pdf_filename = os.path.join(folder, settings['output']['name'] + '.pdf')
    with open(dot_filename, 'r') as dotfile, open(pdf_filename, 'wb') as pdffile:
        subprocess.run(['dot', '-Tpdf'], check=True, stdin=dotfile, stdout=pdffile)

if __name__ == '__main__':

    main()

