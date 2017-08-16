from types import MappingProxyType
from snutree.api import deep_update

def test_empty():
    dict1 = {}
    dict2 = {'a' : 1, 'b' : {'c: 2'}, 'd' : [3]}
    deep_update(dict1, dict2)
    assert dict1 == dict2

def test_partitioned():
    dict1 = {'b' : {}}
    dict2 = {'a' : {}}
    updated = {'a' : {}, 'b' : {}}
    deep_update(dict1, dict2)
    assert dict1 == updated

def test_immutable_sequence():
    # Strings with the same path in both dictionaries should not be
    # appended (i.e., only actual lists---or, more specifically, mutable
    # sequences---should be appended to each other)
    dict1 = {1 : 'abc'}
    dict2 = {1 : 'def'}
    deep_update(dict1, dict2)
    assert dict1 == dict2

def test_immutable_mapping():
    # The same should apply to immutable mappings
    dict3 = {1 : MappingProxyType({2 : 3})}
    dict4 = {1 : MappingProxyType({3 : 2})}
    deep_update(dict3, dict4)
    assert dict3 == dict4

def test_simple():
    dict1 = dict(
            a=1,
            b=2,
            c=None,
            d=dict(
                e=3,
                d=5,
                f=[1, 2, None, 3]
                )
            )
    dict2 = dict(
            e=5,
            d=dict(
                e=4,
                d=2,
                f=[5, 2]
                )
            )
    updated = dict(
            a=1,
            b=2,
            c=None,
            d=dict(
                e=4,
                d=2,
                f=[1, 2, None, 3, 5, 2]
                ),
            e=5
            )
    deep_update(dict1, dict2)
    assert dict1 == updated

