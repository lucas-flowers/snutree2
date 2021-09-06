from dataclasses import dataclass
from pathlib import Path

import pytest
from _pytest.config import Config

from snutree.config import api
from tests.conftest import TestCase


@dataclass
class ExampleTestCase(TestCase):
    @property
    def name(self) -> str:
        return self.id


@pytest.mark.parametrize(
    "case",
    [
        ExampleTestCase("sigmanu_basic"),
    ],
)
def test_examples(pytestconfig: Config, case: ExampleTestCase) -> None:

    root = Path(__file__).parent
    input_path = (root / "input" / case.name).with_suffix(".csv")
    actual = api.run(input_path)
    expected_path = (root / "output" / case.name).with_suffix(".dot")

    # Do not directly assert equality, to avoid generating pytest comparison
    # output, which is really slow for the large files used in these test cases
    if not expected_path.exists() or actual != expected_path.read_text():
        overwrite: bool = pytestconfig.getoption("--overwrite")
        if overwrite:
            expected_path.write_text(actual)
            pytest.fail("output changed; overwrote sample file")
        else:
            pytest.fail("output changed")
