
from collections import OrderedDict
from types import MappingProxyType

import pytest

from snutree.utilities import deep_update

@pytest.mark.parametrize('dicts, expected', [

    # No dicts
    [
        (),
        {},
    ],

    # Empty dicts
    [
        ({},),
        {},
    ],
    [
        ({}, {}, {}),
        {},
    ],

    # Scalars, basic
    [
        ({'a': 1}, {'a': 2}, {'a': 3}),
        {'a': 3},
    ],

    # Null overrides scalars
    [
        ({'a': 1}, {'a': 2}, {'a': None}),
        {'a': None},
    ],

    # Lists, basic
    [
        ({'a': [1]}, {'a': [2]}, {'a': [3]}),
        {'a': [1, 2, 3]},
    ],

    # Null does not modify lists
    [
        ({'a': [1]}, {'a': None}, {'a': [2]}),
        {'a': [1, 2]},
    ],

    # Scalars override lists
    [
        ({'a': [1, 2, 3]}, {'a': 5}),
        {'a': 5},
    ],

    # Strings are treated like scalars, not lists
    [
        ({'a': 'in'}, {'a': 'love'}, {'a': 'palisades'}),
        {'a': 'palisades'},
    ],

    # Dicts, basic
    [
        ({'a': {'b': 1}}, {'a': {'b': 2}}, {'a': {'c': 3}}),
        {'a': {'b': 2, 'c': 3}},
    ],

    # Null does not modify dicts
    [
        ({'a': {'b': 1}}, {'a': None}, {'a': {'c': 2}}),
        {'a': {'b': 1, 'c': 2}},
    ],

    # Scalars override dicts
    [
        ({'a': {'a': 1, 'b': 2, 'c': 3}}, {'a': 5}),
        {'a': 5},
    ],

    # Immutable maps are treated like scalars, not dicts
    [
        (
            {'a': MappingProxyType({'oh': 'how'})},
            {'a': MappingProxyType({'i': 'meant'})},
            {'a': MappingProxyType({'no': 'harm'})},
        ),
        {'a': MappingProxyType({'no': 'harm'})},
    ],

    # Null-valued items in later subcollections have no effect
    [
        ({'a': {'b': []}}, {'a': {'b': None}}, {'a': None}, None),
        {'a': {'b': []}},
    ],

    # But other falsy-valued items in later subcollections do have an effect
    [
        ({'a': {'b': []}}, {'a': {'b': ''}}, {'a': ''}),
        {'a': ''},
    ],

    # More complex test
    [
        (
            {'a': 1, 'b': 2, 'c': None, 'd': {'e': 3, 'd': 5, 'f': [1, 2, None, 3]}},
            {'e': 5, 'd': {'e': 4, 'd': 2, 'f': [5, 2]}},
        ),
        {'a': 1, 'b': 2, 'c': None, 'd': {'e': 4, 'd': 2, 'f': [1, 2, None, 3, 5, 2]}, 'e': 5},
    ],

])
def test_deep_update(dicts, expected):
    assert OrderedDict(deep_update(*dicts)) == OrderedDict(expected)

