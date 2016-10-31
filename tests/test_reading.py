from nose.tools import *
# from family_tree.reading import *

# def test_read_chapters():
#
#     chapters = read_chapters('chapters.csv')
#     assert_equal(chapters['Alpha'], 'Virginia Military Institute')
#     assert_equal(chapters['Delta Zeta'], 'Western Reserve University')

# def test_read_members():
#
#     graph = read_members('directory.csv')
#     assert_equal(graph.node['1352']['record'].name, 'Lucas Flowers')
#
#     records = read_members('brothers_not_knights.csv')

# def test_read_transfers():
#
#     records = read_members('directory.csv')
#     chapters = read_chapters('chapters.csv')
#
#     assert_equal(records['0986'].parent_keys[0], 'Kappa Delta')
#     assert_equal(read_transfers(records, chapters).popitem()[0], 'Kappa Delta (Spring 1983)')
#     assert_equal(records['0986'].parent_keys[0], 'Kappa Delta (Spring 1983)')
#
# def test_read():
#
#     records = read('directory.csv', 'chapters.csv', 'brothers_not_knights.csv')
#
#
#
#
#
#
#
