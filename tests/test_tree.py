from unittest import TestCase
from functools import partial
from snutree.schemas.basic import KeylessMember
from snutree.tree import FamilyTree, TreeError, TreeErrorCode

class TestTree(TestCase):

    def setUp(self):

        self.member1 = KeylessMember.from_dict({
            'name' : 'Bob Dole',
            'pledge_semester' : 'Fall 2000',
            # 'big_name' : None,
            })

        self.member2 = KeylessMember.from_dict({
            'name' : 'Rob Cole',
            'pledge_semester' : 'Fall 2001',
            'big_name' : 'Bob Dole',
            })

        self.members = [self.member1, self.member2]

    def assertRaisesTreeErrorWithCode(self, code, func):
        with self.assertRaises(TreeError) as cm:
            func()
        self.assertEqual(cm.exception.errno, code)

    def test_duplicate_entity(self):

        self.member2.key = 'Bob Dole'
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.DUPLICATE_ENTITY,
                partial(FamilyTree, self.members)
                )

    def test_parent_unknown(self):

        self.member1.parent = 'Hipster Band'
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.PARENT_UNKNOWN,
                partial(FamilyTree, self.members)
                )

    def test_parent_not_prior(self):

        self.member1.semester += 1000
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.PARENT_NOT_PRIOR,
                partial(FamilyTree, self.members)
                )

    def test_unknown_edge_component(self):

        settings = {'edges' : [{
            'nodes' : ['Bob Dole', 'Rob Cole', 'Carmen Sandiego']
            }]}

        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.UNKNOWN_EDGE_COMPONENT,
                partial(FamilyTree, self.members, settings=settings)
                )

    def test_cycle(self):

        self.member1.parent = 'Bob Dole'
        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.CYCLE,
                partial(FamilyTree, self.members)
                )

    def test_family_color_conflict(self):

        settings = {'family_colors' : {
            'Bob Dole' : 'blue',
            'Rob Cole' : 'yellow'
            }}

        self.assertRaisesTreeErrorWithCode(
                TreeErrorCode.FAMILY_COLOR_CONFLICT,
                partial(FamilyTree, self.members, settings=settings)
                )

