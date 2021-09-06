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

    root = Path(__file__).parent / "examples" / case.name

    input_path = root / "input.csv"
    output_path = root / "output.dot"

    actual = api.run(input_path)

    # Do not directly assert equality, to avoid generating pytest comparison
    # output, which is really slow for the large files used in these test cases
    if not output_path.exists() or actual != output_path.read_text():
        overwrite: bool = pytestconfig.getoption("--overwrite")
        if overwrite:
            output_path.write_text(actual)
            pytest.fail("output changed; overwrote sample file")
        else:
            pytest.fail("output changed")
