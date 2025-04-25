import argparse
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from snutree.api import SnutreeApi


class Args(BaseModel):
    input_files: list[Path]
    config: Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate family tree.")

    parser.add_argument(
        "input_files",
        metavar="INPUT_FILES",
        type=Path,
        nargs="*",
        help="Input files to process (e.g., .csv, .json, .sql)",
    )

    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Config file path",
    )

    raw: object = vars(parser.parse_args())

    args = Args.model_validate(raw)

    api: SnutreeApi[Any, Any]  # type: ignore[explicit-any]

    api = SnutreeApi.from_path(args.config)

    output = api.run(args.input_files)  # type: ignore[misc]

    print(output)
