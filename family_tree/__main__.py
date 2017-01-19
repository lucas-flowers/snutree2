from family_tree.directory import Directory

directory_path = 'directory.csv'
bnks_path = 'brothers_not_knights.csv'
affiliations_path = 'affiliations.csv'
settings_path = 'settings.yaml'

# CSV -> intermediate
directory = Directory.from_paths(
        directory_path,
        bnks_path,
        affiliations_path,
        settings_path,
        )

tree = directory.to_tree()
tree.decorate()
dotgraph = tree.to_dot_graph()

print(dotgraph.to_dot())

