import argparse
from pathlib import Path

from pydantic import BaseModel

from snutree.api import SnutreeApi
from snutree.model.rank import Rank


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

    api: SnutreeApi[Rank, object] = SnutreeApi.from_path(args.config)

    output = api.run(args.input_files)

    print(output)
