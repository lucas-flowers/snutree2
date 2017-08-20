import pytest
from snutree.schemas.basic import KeylessMember
from snutree.tree import FamilyTree
from snutree.writers.dot import add_colors, add_custom_edges
from snutree.errors import SnutreeWriterError

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

def test_unknown_edge_component(members):
    edges = [{ 'nodes' : ['Bob Dole', 'Rob Cole', 'Carmen Sandiego'] }]
    tree = FamilyTree(members)
    with pytest.raises(SnutreeWriterError):
        add_custom_edges(tree, edges)

def test_family_color_conflict(members):
    family_colors = { 'Bob Dole' : 'blue', 'Rob Cole' : 'yellow' }
    tree = FamilyTree(members)
    with pytest.raises(SnutreeWriterError):
        add_colors(tree, family_colors)

