
from itertools import repeat

import pytest
from jsonschema.exceptions import ValidationError

from conftest import trim
from snutree.write import dot
from snutree.model.dot import Graph, Node, Edge
from snutree.write.dot.config import class_map, validate
from snutree.model.tree import Entity, Relationship, Cohort, FamilyTree

@pytest.mark.parametrize('keys, error', [

    ([], False),

    (['root'], False),
    (['tree'], False),
    (['rank'], False),
    (['custom'], False),

    (['root', 'tree'], False),
    (['root', 'rank'], False),
    (['root', 'custom'], False),

    (['tree', 'root'], True),
    (['tree', 'rank'], False),
    (['tree', 'custom'], False),

    (['rank', 'root'], True),
    (['rank', 'tree'], False),
    (['rank', 'custom'], False),

    (['custom', 'root'], True),
    (['custom', 'tree'], True),
    (['custom', 'rank'], True),

    (['root', 'tree', 'rank', 'custom_a', 'custom_b'], False),
    (['root', 'custom_a', 'tree', 'rank', 'custom_b'], True),

])
def test_class_map(keys, error):
    mapping = {key: {} for key in keys}
    if not error:
        class_map(mapping)
    else:
        with pytest.raises(ValueError):
            class_map(mapping)

@pytest.mark.parametrize('config', [
    {},
    {'class': {}},
    {'class': {'node': {}}},
    {'class': {'node': {'custom_class': {}}}},
    {'class': {'node': {'custom_class': {'color': 'orange'}}}},
])
def test_config_validate(config):
    validate(config)

@pytest.mark.parametrize('config', [
    {'class': {'graph': {'custom_class': {}}}}, # No custom graphs
    {'class': {'node': {'custom': {}, 'root': {}}}}, # Root must go first
])
def test_config_validate_invalid(config):
    with pytest.raises(ValidationError):
        validate(config)

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
        {'class': {'edge': {'nonexistent': {'color': 'blue'}}}},
        {},
    ),

    # Class is defined but not used
    (
        'node', {}, {},
        {'class': {'node': {'nonexistent': {'color': 'blue'}}}},
        {},
    ),

    # Class is defined and used
    (
        'node', {'class'}, {},
        {'class': {'node': {'class': {'color': 'blue'}}}},
        {'color': 'blue'},
    ),

    # Order of attributes in the config dict is preserved
    (
        'node', {'class'}, {},
        {'class': {'node': {'class': {'size': 10, 'color': 'blue'}}}},
        {'size': 10, 'color': 'blue'},
    ),
    (
        'node', {'class'}, {},
        {'class': {'node': {'class': {'color': 'blue', 'size': 10}}}},
        {'color': 'blue', 'size': 10},
    ),

    # The last class in the config takes priority when there are conflicts
    (
        'node', {'class_a', 'class_b'}, {},
        {'class': {'node': {'class_a': {'color': 'blue'}, 'class_b': {'color': 'red'}}}},
        {'color': 'red'},
    ),
    (
        'node', {'class_b', 'class_a'}, {},
        {'class': {'node': {'class_b': {'color': 'red'}, 'class_a': {'color': 'blue'}}}},
        {'color': 'blue'},
    ),

    # Attribute order still reflects config order when there are conflicts
    (
        'node', {'class_a', 'class_b'}, {},
        {'class': {'node': {'class_a': {'A': 'a', 'B': 'b'}, 'class_b': {'B': 2, 'A': 1}}}},
        {'A': 1, 'B': 2},
    ),

    # The 'label' field is a template whose values are filled by the data dict
    (
        'edge', {'class'}, {'name': 'Test'},
        {'class': {'edge': {'class': {'label': 'Name is {name}', 'title': 'Title is {name}'}}}},
        {'label': 'Name is Test', 'title': 'Title is {name}'},
    ),

    # Fields for classes corresponding to subgraphs are not included, since
    # they are written as attribute statements for the whole subgraph....
    (
        'node', {'tree', 'other_class'}, {},
        {'class': {'node': {'tree': {'color': 'red'}, 'other_class': {'fillcolor': 'blue'}}}},
        {'fillcolor': 'blue'},
    ),

    # .... *except* for the label
    (
        'node', {'tree', 'other_class'}, {},
        {'class': {'node': {'tree': {'label': 'The Label'}, 'other_class': {'fillcolor': 'blue'}}}},
        {'label': 'The Label', 'fillcolor': 'blue'},
    ),

])
def test_component_attributes(component_type, classes, data, config, expected):
    write = dot.Write(config)
    component = write.attribute_list(component_type, classes, data)
    assert component == expected

@pytest.mark.parametrize('graph_id, config, expected', [

    # Empty config
    (
        '',
        {},
        [],
    ),

    # No attributes defined at all
    (
        'root',
        {},
        [],
    ),

    # Attributes defined but not used
    (
        'root',
        {'class': {'node': {'tree': {'a': 1}}}},
        [],
    ),

    # Graph exists in config but is undefined
    (
        'root',
        {'class': {'graph': {'root': {}}}},
        [],
    ),

    # Attributes defined and used
    (
        'root',
        {'class': {'graph': {'root': {'a': 1}}}},
        [Graph(a=1)],
    ),
    (
        'root',
        {'class': {'node': {'root': {'a': 1}}}},
        [Node(a=1)],
    ),
    (
        'root',
        {'class': {'edge': {'root': {'a': 1}}}},
        [Edge(a=1)],
    ),
    (
        'root',
        {'class': {'graph': {'root': {'a': 1}}, 'node': {'root': {'b': 2}}, 'edge': {'root': {'c': 3}}}},
        [Graph(a=1), Node(b=2), Edge(c=3)],
    ),

    # The 'label' attribute is not included in attribute statements for nodes
    # and edges (since they will be included in attribute lists)
    (
        'root',
        {'class': {'graph': {'root': {'label': 'The Label'}}}},
        [Graph(label='The Label')],
    ),
    (
        'root',
        {'class': {'node': {'root': {'label': 'The Label'}}}},
        [],
    ),
    (
        'root',
        {'class': {'edge': {'root': {'label': 'The Label'}}}},
        [],
    ),

])
def test_attribute_statements(graph_id, config, expected):
    write = dot.Write(config)
    component = write.attribute_statements(graph_id)
    assert component == expected

def test_family_tree_standard_order():
    '''
    Nodes are ordered by family, in ascending order of key. Edges are sorted by
    ascending order of parent key, then by child key.
    '''

    tree = FamilyTree(
        entities=[
            Entity(id) for id in [
                'c3', 'c2', 'c1',
                'b3', 'b2', 'b1',
                'a3', 'a2', 'a1',
            ]
        ],
        relationships=[
            Relationship(from_id, to_id) for from_id, to_id in [
                ('b3', 'a2'),
                ('c3', 'b2'), ('b2', 'a1'), ('c3', 'a1'),
                ('c2', 'b1'),
            ]
        ],
    )

    assert dot.write(tree) == trim(r'''
        digraph "root" {
            subgraph "tree" {
                "a1";
                "b2";
                "c3";
                "a2";
                "b3";
                "a3";
                "b1";
                "c2";
                "c1";
                "b2" -> "a1";
                "b3" -> "a2";
                "c2" -> "b1";
                "c3" -> "a1";
                "c3" -> "b2";
            }
        }
    ''')

@pytest.mark.parametrize('', repeat((), times=10))
def test_family_tree_shuffled_order():
    '''
    When a seed is provided, nodes are grouped into internally-sorted families.
    The families themselves are shuffled based on the seed. Resulting code is
    consistent across different calls to dot.write.
    '''

    tree = FamilyTree(
        entities=[
            Entity(id)
            for id in 'abcdefg'
        ],
        relationships=[
            Relationship(from_id, to_id)
            for from_id, to_id in ['cd', 'ce']
        ],
    )

    config = {
        'seed': 1066,
    }

    assert dot.write(tree, config) == trim(r'''
        digraph "root" {
            subgraph "tree" {
                "f";
                "g";
                "c";
                "d";
                "e";
                "b";
                "a";
                "c" -> "d";
                "c" -> "e";
            }
        }
    ''')

def test_family_tree_no_cohorts():

    tree = FamilyTree(
        entities=[
            Entity(id, classes, data)
            for id, classes, data in [
                ('I', ['root', 'tree', 'emperor'], {'name': 'Irene Sarantapechaina'}),
                ('N', ['root', 'tree', 'emperor'], {'name': 'Nikephoros I'}),
            ]
        ],
        relationships=[
            Relationship(from_id, to_id, classes, data)
            for from_id, to_id, classes, data in [
                ('I', 'N', ['root', 'tree'], {'name': 'Succession'}),
            ]
        ],
    )

    config = {
        'class': {
            'node': {
                'emperor': {
                    'label': '{name}',
                },
            },
            'edge': {
                'tree': {
                    'label': '{name}',
                    'color': 'red',
                },
            },
            'graph': {
                'root': {
                    'rankdir': 'LR',
                },
            },
        },
        'custom': {
            'node': {
                'R': {
                    'label': 'Nero',
                    'color': 'pink',
                },
            },
            'edge': {
                'R,N': {
                    'label': '???',
                },
            },
        },
    }

    assert dot.write(tree, config) == trim(r'''
        digraph "root" {
            graph [rankdir="LR"];
            subgraph "tree" {
                edge [color="red"];
                "I" [label="Irene Sarantapechaina"];
                "N" [label="Nikephoros I"];
                "R" [label="Nero",color="pink"];
                "I" -> "N" [label="Succession"];
                "R" -> "N" [label="???"];
            }
        }''')

def test_family_tree_complete():

    tree = FamilyTree(
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
        cohorts=[
            Cohort(rank, ids, classes, data)
            for rank, ids, classes, data in [
                ('960s', ['N', 'J'], {}, {}),
                ('970s', ['B'], {}, {}),
            ]
        ],
    )

    config = {
        'class': {
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
                'root': {
                    'color': 'purple',
                },
                'usurper': {
                    'style': 'dotted',
                    'color': 'yellow',
                },
            },
        },
    }

    assert dot.write(tree, config) == trim(r'''
        digraph "root" {
            edge [color="purple"];
            subgraph "rankL" {
                "960sL";
                "970sL";
                "960sL" -> "970sL";
            }
            subgraph "tree" {
                "B" [label="Basil II",color="purple"];
                "J" [label="John Tzimiskes: The Usurper",color="red"];
                "N" [label="Nikephoros Phokas",color="purple"];
                "J" -> "B";
                "N" -> "J" [style="dotted",color="yellow"];
            }
            subgraph "rankR" {
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

