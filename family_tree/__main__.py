import networkx as nx
import pydotplus.graphviz as gz

from family_tree.reading import read, records_to_tree
from family_tree.semester import *
from family_tree.writing import *


records = read('directory.csv', 'chapters.csv', 'brothers_not_knights.csv')
graph = records_to_tree(records)
dotgraph = create_graph(graph, records)

print(dotgraph.to_dot())

