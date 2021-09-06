from dataclasses import dataclass
from itertools import chain

import pytest
from _pytest.config import Config

from snutree.api import SnutreeApi, SnutreeApiProtocol
from tests.conftest import TestCase


@dataclass
class ExampleTestCase(TestCase):

    output_name: str

    @property
    def name(self) -> str:
        return self.id


@pytest.mark.parametrize(
    "case",
    [
        ExampleTestCase(
            id="sigmanu_basic",
            output_name="sigmanu_basic.dot",
        ),
        ExampleTestCase(
            id="keyed",
            output_name="keyed.dot",
        ),
    ],
)
def test_examples(pytestconfig: Config, case: ExampleTestCase) -> None:

    root_path = pytestconfig.rootpath / "examples" / case.name
    input_paths = chain(root_path.rglob("*.csv"), root_path.rglob("*.json"))
    output_path = root_path / case.output_name

    module_name = ".".join(["examples", case.name, "config"])
    api: SnutreeApiProtocol = SnutreeApi.from_module_name(module_name)
    actual = api.run(input_paths)

    # Do not directly assert equality, to avoid generating pytest comparison
    # output, which is really slow for the large files used in these test cases
    if not output_path.exists() or actual != output_path.read_text():
        overwrite: bool = pytestconfig.getoption("--overwrite")
        if overwrite:
            output_path.write_text(actual)
            pytest.fail("output changed; overwrote sample file")
        else:
            pytest.fail("output changed")
