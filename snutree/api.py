import importlib
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from io import TextIOWrapper
from itertools import chain
from os import PathLike
from pathlib import Path
from typing import IO, Generic, Protocol, TypeVar, Union

from snutree.model.entity import CustomEntity, Entity, EntityId
from snutree.model.rank import AnyRank
from snutree.model.tree import FamilyTree, FamilyTreeConfig
from snutree.reader import Reader, ReaderConfigs
from snutree.reader.csv import CsvReader
from snutree.reader.json import JsonReader
from snutree.reader.sql import SqlReader
from snutree.writer.dot import DotWriter, DotWriterConfig

M = TypeVar("M")


class Parser(Protocol[AnyRank, M]):
    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[Entity[AnyRank, M]]:
        ...


class Writer(Protocol[AnyRank, M]):
    def write(self, tree: FamilyTree[AnyRank, M]) -> str:
        ...


InputFile = Union[
    Path,
    IO[str],
    tuple[TextIOWrapper, str],
]


@dataclass
class SnutreeConfig(Generic[AnyRank, M]):
    rank_type: type[AnyRank]
    parser: Parser[AnyRank, M]
    tree: FamilyTreeConfig[AnyRank]
    writer: DotWriterConfig[AnyRank, M]
    readers: ReaderConfigs = field(default_factory=ReaderConfigs)

    custom_entities: list[CustomEntity[AnyRank, M]] = field(default_factory=list)
    custom_relationships: set[tuple[str, str]] = field(default_factory=set)


class SnutreeApiProtocol(Protocol):
    def run(self, input_files: Iterable[InputFile]) -> str:
        ...


@dataclass
class SnutreeApi(Generic[AnyRank, M]):
    rank_type: type[AnyRank]
    readers: list[Reader]
    parser: Parser[AnyRank, M]
    tree_config: FamilyTreeConfig[AnyRank]
    writer: Writer[AnyRank, M]

    custom_entities: list[CustomEntity[AnyRank, M]]
    custom_relationships: set[tuple[str, str]]

    @classmethod
    def from_config(cls, config: SnutreeConfig[AnyRank, M]) -> "SnutreeApi[AnyRank, M]":
        return cls(
            rank_type=config.rank_type,
            readers=[
                CsvReader(),
                JsonReader(),
                *([SqlReader(config.readers.sql)] if config.readers.sql is not None else []),
            ],
            parser=config.parser,
            tree_config=config.tree,
            writer=DotWriter(config.writer),
            custom_entities=config.custom_entities,
            custom_relationships=config.custom_relationships,
        )

    @classmethod
    def from_module(cls, module_name: str) -> "SnutreeApi[AnyRank, M]":
        module = importlib.import_module(module_name)
        config: object = getattr(module, "__snutree__")
        assert isinstance(config, SnutreeConfig)
        return cls.from_config(config)

    def read(self, input_files: Iterable[InputFile]) -> Iterator[tuple[IO[str], str]]:
        for input_file in input_files:
            if isinstance(input_file, PathLike):
                with input_file.open("r") as f:
                    yield f, input_file.suffix
            elif isinstance(input_file, IO):
                yield input_file, input_file.name
            else:
                yield input_file

    def run(self, input_files: Iterable[InputFile]) -> str:
        readers = {extension: reader for reader in self.readers for extension in reader.extensions}

        rows = (row for input_file, extension in self.read(input_files) for row in readers[extension].read(input_file))

        entities = self.parser.parse(rows)

        tree = FamilyTree(
            rank_type=self.rank_type,
            entities=chain(entities, self.custom_entities),
            relationships={(EntityId(a), EntityId(b)) for a, b in self.custom_relationships},
            config=self.tree_config,
        )

        return self.writer.write(tree)
