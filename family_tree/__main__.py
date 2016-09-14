import networkx as nx

from family_tree.semester import *
from family_tree.writing import *
from family_tree import tree

# Initialization

graph = tree.generate_graph('directory.csv', 'chapters.csv', 'brothers_not_knights.csv', 'family_colors.csv')
tree.decorate_tree(graph)
dotgraph = create_graph(graph)

print(dotgraph.to_dot())

