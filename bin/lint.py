#!/usr/bin/env python

import re
import subprocess
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager, nullcontext
from itertools import chain
from subprocess import CompletedProcess
from typing import (
    ClassVar,
    ContextManager,
    Dict,
    Iterator,
    List,
    Optional,
    Protocol,
    Type,
    runtime_checkable,
)
from uuid import uuid4


class Linter(ABC):

    subclasses: ClassVar[List[Type["Linter"]]] = []
    name: ClassVar[str]

    def __init_subclass__(cls) -> None:
        cls.subclasses.append(cls)

    @classmethod
    @abstractmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        ...

    @classmethod
    def execute(cls, verbose: bool, fast: bool) -> Optional[CompletedProcess[str]]:
        command = cls.command(verbose=verbose, fast=fast)
        return (
            None
            if command is None
            else subprocess.run(
                command,
                shell=True,
                capture_output=True,
                check=False,
                encoding="utf-8",
                text=True,
            )
        )

    @classmethod
    def execute_all(cls, verbose: bool, fast: bool) -> Dict[Type["Linter"], Optional[CompletedProcess[str]]]:
        results: Dict[Type[Linter], Optional[CompletedProcess[str]]] = {}
        with ThreadPoolExecutor() as executor:
            future_to_linter = {
                executor.submit(linter.execute, verbose=verbose, fast=fast): linter for linter in cls.subclasses
            }
            for future in as_completed(future_to_linter):
                linter = future_to_linter[future]
                results[linter] = future.result()
        # Recreate the dict so that it is in the same order as cls.subclasses
        return {linter: results[linter] for linter in cls.subclasses}


class RstLint(Linter):

    name = "rst-lint"

    @classmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        return "rst-lint ."


class Mypy(Linter):

    name = "mypy"

    @classmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        if fast:
            return None
        else:
            return f"{cls.name} ."


class Pylint(Linter):

    name = "pylint"

    @classmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        reports = "--reports yes" if verbose else ""
        if fast:
            return None
        else:
            return fr"""{cls.name} {reports} $(find . -name '*.py' -or -name '*.pyi')"""


class Flake8(Linter):

    name = "flake8"

    @classmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        verbose_flag = "--verbose" if verbose else ""
        return f"{cls.name} {verbose_flag}"


class Isort(Linter):

    name = "isort"

    @classmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        if fast:
            return None
        else:
            quiet = "--quiet" if not verbose else ""
            show_files = "--show-files" if verbose else ""
            return f"{cls.name} --check-only {quiet} {show_files} ."


class YamlLint(Linter):

    name = "yamllint"

    @classmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        return f"{cls.name} --strict ."


class Black(Linter):

    name = "black"

    @classmethod
    def command(cls, verbose: bool, fast: bool) -> Optional[str]:
        if fast:
            return None
        else:
            quiet = "--quiet" if not verbose else ""
            return f"{cls.name} {quiet} --check ."


def git_stash_save(stash_name: str) -> None:

    args = [
        "git",
        "stash",
        "save",
        "--quiet",
        "--include-untracked",
        "--keep-index",
        stash_name,
    ]

    subprocess.run(
        args,
        text=True,
        capture_output=False,
        check=True,
    )


def git_stash_pop(stash_name: str) -> None:

    result = subprocess.run(
        ["git", "stash", "list"],
        text=True,
        capture_output=True,
        check=True,
    )

    stash_line: Optional[str] = None
    for line in result.stdout.splitlines():
        if stash_name in line:
            stash_line = line
            break

    if stash_line is not None:
        match = re.match(r"stash@\{(?P<stash_revision>.+?)\}", stash_line)
        if match:
            stash_revision = match.group("stash_revision")
            subprocess.run(
                ["git", "stash", "pop", "--quiet", f"stash@{{{stash_revision}}}"],
                text=True,
                capture_output=False,
                check=True,
            )


@contextmanager  # type: ignore[misc]
def stashed(stash_name: str) -> Iterator[None]:
    git_stash_save(stash_name)
    try:
        yield
    finally:
        git_stash_pop(stash_name)


def run_linters(verbose: bool, fast: bool) -> int:

    results = Linter.execute_all(verbose, fast)

    max_name_length = max(len(linter.name) for linter in Linter.subclasses)

    returncode = 0
    for linter, result in results.items():

        if result is None:
            lines = ["🟡 Skipped"]
        elif verbose or result.returncode:
            raw_lines = list(chain(result.stdout.splitlines(), result.stderr.splitlines())) or ["Failed"]
            lines = [f"🔴 {line}" for line in raw_lines]
            if result.returncode:
                returncode = 1
        else:
            lines = ["🟢 Good"]

        prefix = f"{linter.name}: "
        spaces = " " * (max_name_length - len(linter.name))
        for line in lines:
            print(f"{prefix}{spaces}{line}")

    return returncode


@runtime_checkable
class Args(Protocol):
    fast: bool
    verbose: bool
    stash: bool


def parse_args() -> Args:

    parser = ArgumentParser()

    parser.add_argument(
        "--fast",
        action="store_true",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
    )

    parser.add_argument(
        "--stash",
        action="store_true",
    )

    args = parser.parse_args()
    assert isinstance(args, Args)
    return args


def main() -> None:

    args = parse_args()

    context: ContextManager[None]
    if args.stash:
        context = stashed(f"lint-{uuid4()}")
    else:
        context = nullcontext()

    with context:
        returncode = run_linters(verbose=args.verbose, fast=args.fast)

    sys.exit(returncode)


if __name__ == "__main__":
    main()
