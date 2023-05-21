from dataclasses import dataclass
from inspect import cleandoc

from _pytest.config import Config
from _pytest.config.argparsing import Parser


@dataclass
class TestCase:
    __test__ = False
    id: str


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--overwrite",
        action="store_true",
        help="Update expected results for approval/regression tests",
    )


def pytest_make_parametrize_id(
    config: Config, val: object, argname: str  # pylint: disable=unused-argument
) -> str | None:
    if isinstance(val, TestCase):
        return val.id
    else:
        return None


def trim(string: str) -> str:
    """
    Remove all leading whitespace, common indentation, and trailing whitespace
    (except for the final, standard newline).
    """
    return cleandoc(string) + "\n"
