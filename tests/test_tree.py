from unittest import TestCase
from functools import partial
from snutree.schemas.basic import KeylessMember
from snutree.tree import FamilyTree, TreeError, TreeErrorCode
from snutree.directory import Directory

class TestTree(TestCase):

    def setUp(self):

        self.member1 = {
            'name' : 'Bob Dole',
            'pledge_semester' : 'Fall 2000',
            'big_name' : None,
            }

        self.member2 = {
            'name' : 'Rob Cole',
            'pledge_semester' : 'Fall 2001',
            'big_name' : 'Bob Dole',
            }

    # TODO remove all references to Directory from this test and use Member
    # types directly
    @property
    def directory(self):
        return Directory([self.member1, self.member2], [KeylessMember])

    def assertRaisesTreeErrorWithCode(self, code, func):
        with self.assertRaises(TreeError) as cm:
            func()
        self.assertEqual(cm.exception.errno, code)

    def test_duplicate_entity(self):

        self.member2['name'] = 'Bob Dole'
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.DUPLICATE_ENTITY,
                partial(FamilyTree, self.directory)
                )

    def test_parent_unknown(self):

        self.member1['big_name'] = 'Hipster Band'
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.PARENT_UNKNOWN,
                partial(FamilyTree, self.directory)
                )

    def test_parent_not_prior(self):

        self.member1['pledge_semester'] = 'Fall 3000'
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.PARENT_NOT_PRIOR,
                partial(FamilyTree, self.directory)
                )

    def test_unknown_edge_component(self):

        settings = {'edges' : [{
            'nodes' : ['Bob Dole', 'Rob Cole', 'Carmen Sandiego']
            }]}

        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.UNKNOWN_EDGE_COMPONENT,
                partial(FamilyTree, self.directory, settings=settings)
                )

    def test_cycle(self):

        self.member1['big_name'] = 'Bob Dole'
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.CYCLE,
                partial(FamilyTree, self.directory)
                )

    def test_family_color_conflict(self):

        settings = {'family_colors' : {
            'Bob Dole' : 'blue',
            'Rob Cole' : 'yellow'
            }}

        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.FAMILY_COLOR_CONFLICT,
                partial(FamilyTree, self.directory, settings=settings)
                )

