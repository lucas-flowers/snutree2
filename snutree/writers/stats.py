'''
Outputs statistics on the family tree.
'''

import sys

###############################################################################
###############################################################################
#### API                                                                   ####
###############################################################################
###############################################################################

filetypes = {
        'txt',
        }

def compile_tree(tree, RankType, config):

    max_littles = 0
    most_littles = []
    for key, out_degree in tree.graph.out_degree_iter():
        if out_degree > max_littles:
            most_littles = [key]
            max_littles = out_degree
        elif out_degree == max_littles:
            most_littles.append(key)

    output_fields = {
            'members' : tree.graph.number_of_nodes(),
            'relationships' : tree.graph.number_of_edges(),
            'singletons' : len(list(tree.singletons())),
            'max_littles' : max_littles,
            'most_littles' : most_littles,
            }

    output = '\n'.join('{key}={value}'.format(key=key, value=value) for key, value in output_fields.items())

    return bytes(output, encoding=sys.getdefaultencoding())




