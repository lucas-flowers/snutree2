
from collections.abc import MutableSequence, MutableMapping

def get(mapping, *args):
    value = mapping
    for arg in args:
        value = value.get(arg, {})
    return value

def deep_update(*dicts):

    def updated_value(old_value, new_value):
        old_map = isinstance(old_value, MutableMapping)
        old_seq = isinstance(old_value, MutableSequence)
        new_map = isinstance(new_value, MutableMapping)
        new_seq = isinstance(new_value, MutableSequence)
        if old_map and new_map:
            return deep_update(old_value, new_value)
        elif old_seq and new_seq:
            return old_value + new_value
        elif (old_map or old_seq) and new_value is None:
            return old_value
        else:
            return new_value

    accumulator = {}
    for dct in dicts:
        accumulator.update({
            key: updated_value(accumulator.get(key), new_value)
            for key, new_value in (dct if dct is not None else {}).items()
        })

    return accumulator

