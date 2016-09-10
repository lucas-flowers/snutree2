import sys
import matplotlib.pyplot as plt
from nose.tools import *
from family_tree.reading import *
from family_tree.tree import *


def test_tree_from_records():

    records = read('directory.csv', 'chapters.csv', 'brothers_not_knights.csv')
    tree = tree_from_records(records)
    a = nx.nx_pydot.to_pydot(tree)
    a.write('out.dot', prog='dot')
    # for node in tree:
    #     if node.record and node.record.key == '1352':
    #         assert_equal(
    #             sorted([child.record.name for child in node]),
    #             ['Aaron Magid', 'John Grezmak', 'Lucas Flowers', 'Tom Kan', 'Zach Palumbo'],
    #             )

