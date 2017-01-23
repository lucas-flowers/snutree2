# import family_tree.csv
import family_tree.sql
from family_tree.tree import FamilyTree

directory_path = 'directory.csv'
bnks_path = 'brothers_not_knights.csv'
affiliations_path = 'affiliations.csv'
settings_path = 'settings.yaml'

############################
                           #

# CSV -> intermediate
directory = family_tree.csv.to_directory(
        directory_path,
        bnks_path,
        affiliations_path,
        settings_path,
        )

############ OR ############

# # SQL -> intermediate
# directory = family_tree.sql.to_directory(
#         settings_path,
#         bnks_path,
#         )

                           #
############################

# Intermediate -> Tree
tree = FamilyTree(directory)

# Tree -> DOT graph
dotgraph = tree.to_dot_graph()

# DOT graph -> stdout
print(dotgraph.to_dot())

