
import pytest

from conftest import trim
from snutree.write import dot
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


