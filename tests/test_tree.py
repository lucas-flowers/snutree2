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
                'pledge_semester' : 'Fall 2000',
                # 'big_name' : None,
                }),
            KeylessMember.from_dict({
                'name' : 'Rob Cole',
                'pledge_semester' : 'Fall 2001',
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

def test_unknown_edge_component(members):
    settings = {'edges' : [{
        'nodes' : ['Bob Dole', 'Rob Cole', 'Carmen Sandiego']
        }]}
    tree = FamilyTree(members, settings=settings)
    from snutree.writers.dot import add_custom_edges
    func = partial(add_custom_edges, tree, settings['edges'])
    code = TreeErrorCode.UNKNOWN_EDGE_COMPONENT
    assert tree_error_code_of(func) == code

# TODO move?
def test_family_color_conflict(members):
    settings = {'family_colors' : {
        'Bob Dole' : 'blue',
        'Rob Cole' : 'yellow'
        }}
    tree = FamilyTree(members, settings=settings)
    from snutree.writers.dot import add_colors
    func = partial(add_colors, tree, settings['family_colors'])
    code = TreeErrorCode.FAMILY_COLOR_CONFLICT
    assert tree_error_code_of(func) == code

