from family_tree.directory import Directory

# Initialization


# CSV -> intermediate
directory = Directory.from_paths(
        'directory.csv',
        'brothers_not_knights.csv',
        'affiliations.csv',
        'settings.yaml'
        )

tree = directory.to_tree()
tree.decorate()
dotgraph = tree.to_dot_graph()

print(dotgraph.to_dot())

