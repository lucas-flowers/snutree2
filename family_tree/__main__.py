from family_tree.tree import FamilyTree
from family_tree.directory import read_settings
from family_tree import csv, sql

settings_path = 'settings.yaml'
settings = read_settings(settings_path)
directory = (sql if 'mysql' in settings else csv).retrieve_directory(settings)
tree = FamilyTree(directory)
dotgraph = tree.to_dot_graph()
print(dotgraph.to_dot())

