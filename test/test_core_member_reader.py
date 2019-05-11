
import pytest

from snutree.core.member.config import Config
from snutree.core.member.model import Member
from snutree.core.member.reader import Reader
from snutree.utilities.semester import Semester

def create_reader(dct):
    config = Config.from_dict(dct, defaults=False, validate=False)
    return Reader(config)

@pytest.mark.parametrize('row, config, expected', [
    (
        {'x': '1'},
        {'id': 'x'},
        '1',
    ),
])
def test_read_id(row, config, expected):
    reader = create_reader(config)
    assert reader.read_id(row) == expected

@pytest.mark.parametrize('row, config, expected', [
    (
        {'x': '1'},
        {'parent_id': 'x'},
        '1',
    ),
])
def test_read_parent_id(row, config, expected):
    reader = create_reader(config)
    assert reader.read_parent_id(row) == expected

@pytest.mark.parametrize('row, config, expected', [

    # Integers
    (
        {'x': '1'},
        {'rank': 'Integer(x)'},
        1,
    ),

    # Semesters
    (
        {'x': 'Fall 2000'},
        {'rank': 'Semester(x)'},
        Semester('Fall 2000'),
    ),

])
def test_read_rank(row, config, expected):
    reader = create_reader(config)
    assert reader.read_rank(row) == expected

@pytest.mark.parametrize('row, config, expected', [

    # Constants
    (
        {},
        {'classes': [
            'clsA',
            'clsB',
            'clsC',
        ]},
        [
            'clsA',
            'clsB',
            'clsC',
        ],
    ),

    # Booleans
    (
        {
            'clsA': '1',
            'clsB': 'TRuE',
            'clsC': '',
            'clsD': 'asdfasdf',
            'clsE': 'yEs',
        },
        {'classes': [
            'Boolean(clsA)',
            'Boolean(clsB)',
            'Boolean(clsC)',
            'Boolean(clsD)',
            'Boolean(clsE)',
        ]},
        [
            'clsA',
            'clsB',
            'clsE',
        ],
    ),

    # Enums
    (
        {
            'A': 'clsA',
            'B': 'clsB',
            'E': 'clsE',
        },
        {'classes': [
            'Enum(A)',
            'Enum(B)',
            'Enum(E)',
        ]},
        [
            'clsA',
            'clsB',
            'clsE',
        ],
    ),

    # Lists
    (
        {
            'listA': ' clsA, clsB  , clsE ',
            'listB': ' ',
            'listC': '',
        },
        {'classes': [
            'List(listA)',
            'List(listB)',
            'List(listC)',
        ]},
        [
            'clsA',
            'clsB',
            'clsE',
        ],
    ),

    # Classes are unique, but in order
    (
        {
            'listA': 'd',
            'listB': 'a,b,c,d,b,d',
        },
        {'classes': [
            'List(listA)',
            'List(listB)',
        ]},
        [
            'd',
            'a',
            'b',
            'c',
        ],
    )

])
def test_read_classes(row, config, expected):
    reader = create_reader(config)
    assert reader.read_classes(row) == expected

@pytest.mark.parametrize('row, config, expected', [

    # Nothing
    (
        {},
        {},
        {},
    ),

    # Unused input
    (
        {
            'id': '84',
            'color': 'blue',
        },
        {'data': {}},
        {},
    ),

    # Calling functions
    (
        {
            'first': 'Brandon',
            'preferred': 'Bran',
            'last': 'Stark',
        },
        {'data': {
            'name': 'PreferredName(first, preferred, last)',
        }},
        {
            'name': 'Bran Stark',
        },
    ),

    # Multiple output rows
    (
        {
            'id': '42',
        },
        {'data': {
            'a': 'id',
            'b': 'id',
            'c': 'id',
        }},
        {
            'a': '42',
            'b': '42',
            'c': '42',
        },
    ),

])
def test_read_data(row, config, expected):
    reader = create_reader(config)
    assert reader.read_data(row) == expected

@pytest.mark.parametrize('row, config, expected', [

    (
        {
            'badge': '1000',
            'big_badge': '950',
            'semester': 'Fall 1950',
            'first': 'Aegon',
            'preferred': 'Jon',
            'last': 'Snow',
            'houses': 'targaryen,stark',
            'snow': 'true',
            'sand': 'false',
        },
        {
            'id': 'badge',
            'parent_id': 'big_badge',
            'rank': 'Semester(semester)',
            'data': {
                'name': 'PreferredName(first, preferred, last)',
            },
            'classes': [
                'List(houses)',
                'Boolean(snow)',
                'Boolean(sand)',
            ],
        },
        Member(
            id='1000',
            parent_id='950',
            rank=Semester('Fall 1950'),
            data={
                'name': 'Jon Snow',
            },
            classes=[
                'targaryen',
                'stark',
                'snow',
            ],
        ),
    ),

])
def test_read_member(row, config, expected):
    reader = create_reader(config)
    assert reader.read_member(row) == expected

