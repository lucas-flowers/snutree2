import argparse
from pathlib import Path

from pydantic import BaseModel

from snutree.api import SnutreeApi, SnutreeConfig


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
        "-c",
        "--config",
        type=Path,
        required=True,
        help="Config file path",
    )

    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=12345,
        help="Seed for random number generation. Provides *some* control over the tree's layout.",
    )

    raw: object = vars(parser.parse_args())

    args = Args.model_validate(raw)

    config = SnutreeConfig.from_path(args.config)

    api = SnutreeApi.from_config(config)

    output = api.run(args.input_files)

    print(output)
