from dataclasses import dataclass
from pathlib import Path

import pytest
from _pytest.config import Config

from snutree.api import SnutreeApi, SnutreeApiProtocol, SnutreeConfig
from tests.conftest import TestCase

ROOT_PATH = Path(__file__).parents[2]


@dataclass
class ExampleTestCase(TestCase):
    module_name: str
    input_paths: list[Path]
    output_path: Path

    @classmethod
    def generate(cls) -> list["ExampleTestCase"]:
        examples = []
        examples_root = ROOT_PATH / "examples"
        for example_path in examples_root.iterdir():
            example_input_paths: list[Path] = []
            if example_path.is_dir():
                for extension in ["csv", "json", "sql"]:
                    example_input_paths.extend(example_path.glob(f"*.{extension}"))
            if example_input_paths:
                examples.append(
                    ExampleTestCase(
                        id=example_path.name,
                        module_name=".".join(["examples", example_path.name, "config"]),
                        input_paths=example_input_paths,
                        output_path=(example_path / example_path.name).with_suffix(".dot"),
                    )
                )
        return examples


@pytest.mark.parametrize("case", ExampleTestCase.generate())
def test_examples(pytestconfig: Config, case: ExampleTestCase) -> None:
    config = SnutreeConfig.from_module(case.module_name)
    api: SnutreeApiProtocol = SnutreeApi.from_config(config, seed=None)
    actual = api.run(case.input_paths, writer_name="dot")

    # Do not directly assert equality, to avoid generating pytest comparison
    # output, which is really slow for the large files used in these test cases
    if not case.output_path.exists() or actual != case.output_path.read_text():
        overwrite: bool = pytestconfig.getoption("--overwrite")
        if overwrite:
            case.output_path.write_text(actual)
            pytest.fail("output changed; overwrote sample file")
        else:
            pytest.fail("output changed")
