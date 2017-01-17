from family_tree.tree import FamilyTree

# Initialization

tree = FamilyTree.from_paths(
        'directory.csv',
        'brothers_not_knights.csv',
        'affiliations.csv',
        'settings.yaml',
        )
tree.decorate()
dotgraph = tree.to_dot_graph()

print(dotgraph.to_dot())

