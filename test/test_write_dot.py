
import pytest

from conftest import trim
from snutree.write import dot
from snutree.model.dot import Node
from snutree.model.tree import Entity, Relationship, Cohort, FamilyTree

@pytest.fixture
def config():
    return {
        'node': {
            'emperor': {
                'label': '{name}',
                'color': 'purple',
            },
            'usurper': {
                'label': '{name}: The Usurper',
                'color': 'red',
            },
        },
        'edge': {
            'family_tree': {
                'color': 'purple',
            },
            'usurper': {
                'style': 'dotted',
                'color': 'yellow',
            },
        },
    }

@pytest.fixture
def tree():
    return FamilyTree(
        entities=[
            Entity(id, classes, data)
            for id, classes, data in [
                ('N', {'emperor'}, {'name': 'Nikephoros Phokas'}),
                ('J', {'emperor', 'usurper'}, {'name': 'John Tzimiskes'}),
                ('B', {'emperor'}, {'name': 'Basil II'}),
            ]
        ],
        relationships=[
            Relationship(from_id, to_id, classes, data)
            for from_id, to_id, classes, data in [
                ('N', 'J', {'usurper', 'succession'}, {}),
                ('J', 'B', {'succession'}, {}),
            ]
        ],
        cohorts= [
            Cohort(rank, ids, classes, data)
            for rank, ids, classes, data in [
                ('960s', ['N', 'J'], {}, {}),
                ('970s', ['B'], {}, {}),
            ]
        ],
        classes=set(),
        data={},
    )

@pytest.mark.parametrize('component_type, classes, data, config, expected', [

    # Empty component
    (
        'node', {}, {},
        {},
        {},
    ),

    # Class is not defined
    (
        'node', {'nonexistent'}, {},
        {},
        {},
    ),

    # Class is defined but not for the right component
    (
        'node', {'nonexistent'}, {},
        {'edge': {'nonexistent': {'color': 'blue'}}},
        {},
    ),

    # Class is defined but not used
    (
        'node', {}, {},
        {'node': {'nonexistent': {'color': 'blue'}}},
        {},
    ),

    # Class is defined and used
    (
        'node', {'class'}, {},
        {'node': {'class': {'color': 'blue'}}},
        {'color': 'blue'},
    ),

    # Order of attributes in the config dict is preserved
    (
        'node', {'class'}, {},
        {'node': {'class': {'size': 10, 'color': 'blue'}}},
        {'size': 10, 'color': 'blue'},
    ),
    (
        'node', {'class'}, {},
        {'node': {'class': {'color': 'blue', 'size': 10}}},
        {'color': 'blue', 'size': 10},
    ),

    # The last class in the config takes priority when there are conflicts
    (
        'node', {'class_a', 'class_b'}, {},
        {'node': {'class_a': {'color': 'blue'}, 'class_b': {'color': 'red'}}},
        {'color': 'red'},
    ),
    (
        'node', {'class_b', 'class_a'}, {},
        {'node': {'class_b': {'color': 'red'}, 'class_a': {'color': 'blue'}}},
        {'color': 'blue'},
    ),

    # Attribute order still reflects config order when there are conflicts
    (
        'node', {'class_a', 'class_b'}, {},
        {'node': {'class_a': {'A': 'a', 'B': 'b'}, 'class_b': {'B': 2, 'A': 1}}},
        {'A': 1, 'B': 2},
    ),

    # The 'label' field is a template whose values are filled by the data dict
    (
        'edge', {'class'}, {'name': 'Test'},
        {'edge': {'class': {'label': 'Name is {name}', 'title': 'Title is {name}'}}},
        {'label': 'Name is Test', 'title': 'Title is {name}'},
    ),

])
def test_component_attributes(component_type, classes, data, config, expected):
    write = dot.Write(config)
    component = write.component_attributes(component_type, classes, data)
    assert component == expected

def test_dot_to_family_tree(tree, config):
    assert dot.write(tree, config) == trim(r'''
        digraph "family_tree" {
            edge [color="purple"];
            subgraph "datesL" {
                "960sL";
                "970sL";
                "960sL" -> "970sL";
            }
            subgraph "members" {
                "N" [label="Nikephoros Phokas",color="purple"];
                "J" [label="John Tzimiskes: The Usurper",color="red"];
                "B" [label="Basil II",color="purple"];
                "N" -> "J" [style="dotted",color="yellow"];
                "J" -> "B";
            }
            subgraph "datesR" {
                "960sR";
                "970sR";
                "960sR" -> "970sR";
            }
            {
                rank="same";
                "960sL";
                "960sR";
                "N";
                "J";
            }
            {
                rank="same";
                "970sL";
                "970sR";
                "B";
            }
        }''')


