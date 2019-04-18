
import pytest
from jsonschema.exceptions import ValidationError

from snutree.write.dot.config import class_map, validate

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

