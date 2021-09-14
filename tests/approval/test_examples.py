from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TextIO

import pytest
from _pytest.config import Config

from snutree.api import SnutreeApi, SnutreeApiProtocol
from tests.conftest import TestCase

ROOT_PATH = Path(__file__).parents[2]


@dataclass
class ExampleTestCase(TestCase):

    module_name: str
    input_paths: list[Path]
    output_path: Path

    def input_files(self) -> Iterable[tuple[TextIO, str]]:
        for input_path in self.input_paths:
            with input_path.open("r") as f:
                yield (f, input_path.suffix)

    @classmethod
    def generate(cls) -> list["ExampleTestCase"]:
        examples = []
        for access_modifier in ["public", "private"]:
            access_modifier_root = ROOT_PATH / "examples" / access_modifier
            if access_modifier_root.exists():
                for example_path in access_modifier_root.iterdir():
                    example_input_paths: list[Path] = []
                    if example_path.is_dir():
                        for extension in ["csv", "json", "sql"]:
                            example_input_paths.extend(example_path.glob(f"*.{extension}"))
                    if example_input_paths:
                        examples.append(
                            ExampleTestCase(
                                id=example_path.name,
                                module_name=".".join(["examples", access_modifier, example_path.name, "config"]),
                                input_paths=example_input_paths,
                                output_path=(example_path / example_path.name).with_suffix(".dot"),
                            )
                        )
        return examples


@pytest.mark.parametrize("case", ExampleTestCase.generate())
def test_examples(pytestconfig: Config, case: ExampleTestCase) -> None:

    api: SnutreeApiProtocol = SnutreeApi.from_module_name(case.module_name)
    actual = api.run(case.input_files())

    # Do not directly assert equality, to avoid generating pytest comparison
    # output, which is really slow for the large files used in these test cases
    if not case.output_path.exists() or actual != case.output_path.read_text():
        overwrite: bool = pytestconfig.getoption("--overwrite")
        if overwrite:
            case.output_path.write_text(actual)
            pytest.fail("output changed; overwrote sample file")
        else:
            pytest.fail("output changed")
