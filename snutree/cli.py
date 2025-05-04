import argparse
from pathlib import Path

from pydantic import BaseModel

from snutree.api import OutputFormat, SnutreeApi, SnutreeConfig


class Args(BaseModel):
    input_files: list[Path]
    format: OutputFormat
    config: Path
    seed: int | None


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
        "-f",
        "--format",
        type=str,
        required=True,
        help="Format that the output will be in",
        choices=OutputFormat.__args__,  # type: ignore[misc,attr-defined] # This does actually exist
    )

    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Seed for random number generation. Provides *some* control over the tree's layout.",
    )

    raw: object = vars(parser.parse_args())

    args = Args.model_validate(raw)

    config = SnutreeConfig.from_path(args.config)

    api = SnutreeApi.from_config(config, seed=args.seed)

    output = api.run(
        input_files=args.input_files,
        writer_name=args.format,
    )

    print(output)
