from dataclasses import dataclass
from typing import Optional

from _pytest.config import Config


@dataclass
class TestCase:
    __test__ = False
    id: str


def pytest_make_parametrize_id(
    config: Config, val: object, argname: str  # pylint: disable=unused-argument
) -> Optional[str]:
    if isinstance(val, TestCase):
        return val.id
    else:
        return None
