
import pytest
from jsonschema.exceptions import ValidationError

from snutree.write.dot.config import Config, class_map

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

    # Nothing at all
    {},

    # Various empty dicts
    {'class': {}},
    {'class': {'node': {}}},
    {'class': {'node': {'custom_class': {}}}},
    {'class': {'node': {'custom_class': {'color': 'orange'}}}},

    # Graphs can have custom classes, but they won't do anything
    {'class': {'graph': {'custom_class': {}}}},

])
def test_config_validate(config):
    assert Config.from_dict(config)

@pytest.mark.parametrize('config', [

    # Root must go first
    {'class': {'node': {'custom': {}, 'root': {}}}},

])
def test_config_validate_invalid(config):
    with pytest.raises(ValidationError):
        Config.from_dict(config)

