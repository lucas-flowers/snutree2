import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Iterable, Protocol, TypeVar

from snutree.model.tree import AnyRank, FamilyTree

E_co = TypeVar("E_co", covariant=True)
E = TypeVar("E")
R = TypeVar("R")


class Reader(Protocol):
    def read(self, path: Path) -> Iterable[dict[str, str]]:
        ...


class Parser(Protocol[E_co]):
    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[E_co]:
        ...


class Assembler(Protocol[E, R, AnyRank]):
    def assemble(self, members: Iterable[E]) -> FamilyTree[E, R, AnyRank]:
        ...


class Writer(Protocol[E, R, AnyRank]):
    def write(self, tree: FamilyTree[E, R, AnyRank]) -> str:
        ...


class SnutreeApiProtocol(Protocol):
    def run(self, input_paths: Iterable[Path]) -> str:
        ...


@dataclass
class SnutreeApi(Generic[E, R, AnyRank]):

    reader: Reader
    parser: Parser[E]
    assembler: Assembler[E, R, AnyRank]
    writer: Writer[E, R, AnyRank]

    @classmethod
    def from_module_name(cls, module_name: str) -> "SnutreeApi[E, R, AnyRank]":
        module = importlib.import_module(module_name)
        api: object = getattr(module, "__snutree__")
        assert isinstance(api, SnutreeApi)
        return api

    def run(self, input_paths: Iterable[Path]) -> str:

        rows = (row for input_path in input_paths for row in self.reader.read(input_path))
        members = self.parser.parse(rows)
        tree = self.assembler.assemble(members)

        return self.writer.write(tree)
