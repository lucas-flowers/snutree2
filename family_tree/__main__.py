import family_tree.csv

directory_path = 'directory.csv'
bnks_path = 'brothers_not_knights.csv'
affiliations_path = 'affiliations.csv'
settings_path = 'settings.yaml'

# CSV -> intermediate
directory = family_tree.csv.to_directory(
        directory_path,
        bnks_path,
        affiliations_path,
        settings_path,
        )

# Intermediate -> Tree
tree = directory.to_tree()

# Tree -> Decorated tree
tree.decorate()

# Tree -> DOT graph
dotgraph = tree.to_dot_graph()

# DOT graph -> stdout
print(dotgraph.to_dot())

