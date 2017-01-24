import os, subprocess
from family_tree.tree import FamilyTree
from family_tree.directory import read_settings
from family_tree import csv, sql

settings_path = 'settings.yaml'
settings = read_settings(settings_path)
directory = (sql if 'mysql' in settings else csv).retrieve_directory(settings)
tree = FamilyTree(directory)
dotgraph = tree.to_dot_graph()
dotcode = dotgraph.to_dot()

folder = settings['output']['directory']

dot_filename = os.path.join(folder, settings['output']['name'] + '.dot')
with open(dot_filename, 'w+') as dotfile:
    dotfile.write(dotcode)

pdf_filename = os.path.join(folder, settings['output']['name'] + '.pdf')
with open(dot_filename, 'r') as dotfile, open(pdf_filename, 'wb') as pdffile:
    subprocess.run(['dot', '-Tpdf'], check=True, stdin=dotfile, stdout=pdffile)

