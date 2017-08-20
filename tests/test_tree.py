from functools import partial
import pytest
from snutree.schemas.basic import KeylessMember
from snutree.tree import FamilyTree, TreeError, TreeErrorCode

# pylint: disable=redefined-outer-name

@pytest.fixture
def members():
    return [
            KeylessMember.from_dict({
                'name' : 'Bob Dole',
                'semester' : 'Fall 2000',
                # 'big_name' : None,
                }),
            KeylessMember.from_dict({
                'name' : 'Rob Cole',
                'semester' : 'Fall 2001',
                'big_name' : 'Bob Dole',
                })
            ]

def tree_error_code_of(func):
    with pytest.raises(TreeError) as exc_info:
        func()
    return exc_info.value.errno

def test_duplicate_entity(members):
    members[1].key = 'Bob Dole'
    func = partial(FamilyTree, members)
    code = TreeErrorCode.DUPLICATE_ENTITY
    assert tree_error_code_of(func) == code

def test_parent_unknown(members):
    members[0].parent = 'Hipster Band'
    func = partial(FamilyTree, members)
    code = TreeErrorCode.PARENT_UNKNOWN
    assert tree_error_code_of(func) == code

def test_parent_not_prior(members):
    members[0].rank += 1000
    func = partial(FamilyTree, members)
    code = TreeErrorCode.PARENT_NOT_PRIOR
    assert tree_error_code_of(func) == code

