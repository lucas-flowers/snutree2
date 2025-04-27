import importlib
import importlib.util
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field, replace
from io import TextIOWrapper
from itertools import chain
from os import PathLike
from pathlib import Path
from typing import IO, Generic, Protocol, TypeVar, Union

from snutree.model.entity import CustomEntity, Entity, EntityId
from snutree.model.rank import AnyRank, Rank
from snutree.model.tree import FamilyTree, FamilyTreeConfig
from snutree.reader import Reader, ReaderConfigs
from snutree.reader.csv import CsvReader
from snutree.reader.json import JsonReader
from snutree.reader.sql import SqlReader
from snutree.writer.dot import DotWriter, DotWriterConfig

MemberT = TypeVar("MemberT")


class Parser(Protocol[AnyRank, MemberT]):
    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[Entity[AnyRank, MemberT]]: ...


class Writer(Protocol[AnyRank, MemberT]):
    def write(self, tree: FamilyTree[AnyRank, MemberT]) -> str: ...


InputFile = Union[
    Path,
    IO[str],
    tuple[TextIOWrapper, str],
]


@dataclass
class SnutreeConfig(Generic[AnyRank, MemberT]):
    rank_type: type[AnyRank]
    parser: Parser[AnyRank, MemberT]
    tree: FamilyTreeConfig[AnyRank]
    writer: DotWriterConfig[AnyRank, MemberT]
    readers: ReaderConfigs = field(default_factory=ReaderConfigs)

    custom_entities: list[CustomEntity[AnyRank, MemberT]] = field(default_factory=list)
    custom_relationships: set[tuple[str, str]] = field(default_factory=set)

    @classmethod
    def from_module(cls, module_name: str) -> "SnutreeConfig[Rank, object]":
        module = importlib.import_module(module_name)
        config: object = getattr(module, "__snutree__")
        assert isinstance(config, SnutreeConfig)
        return config

    @classmethod
    def from_path(cls, path: Path) -> "SnutreeConfig[Rank, object]":
        spec = importlib.util.spec_from_file_location("snutree_config", path)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        assert module is not None
        sys.modules["snutree_config"] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        config: object = getattr(module, "__snutree__")
        assert isinstance(config, SnutreeConfig)
        return config


class SnutreeApiProtocol(Protocol):
    def run(self, input_files: Iterable[InputFile]) -> str: ...


@dataclass
class SnutreeApi(Generic[AnyRank, MemberT]):
    rank_type: type[AnyRank]
    readers: list[Reader]
    parser: Parser[AnyRank, MemberT]
    tree_config: FamilyTreeConfig[AnyRank]
    writer: Writer[AnyRank, MemberT]

    custom_entities: list[CustomEntity[AnyRank, MemberT]]
    custom_relationships: set[tuple[str, str]]

    @classmethod
    def from_config(cls, config: SnutreeConfig[AnyRank, MemberT], seed: int | None) -> "SnutreeApi[AnyRank, MemberT]":
        return cls(
            rank_type=config.rank_type,
            readers=[
                CsvReader(),
                JsonReader(),
                *([SqlReader(config.readers.sql)] if config.readers.sql is not None else []),
            ],
            parser=config.parser,
            tree_config=(config.tree if seed is None else replace(config.tree, seed=seed)),
            writer=DotWriter(config.writer),
            custom_entities=config.custom_entities,
            custom_relationships=config.custom_relationships,
        )

    def read(self, input_files: Iterable[InputFile]) -> Iterator[tuple[IO[str], str]]:
        for input_file in input_files:
            if isinstance(input_file, PathLike):
                with input_file.open("r") as f:
                    yield f, input_file.suffix
            elif isinstance(input_file, IO):
                input_filename: str = input_file.name
                yield input_file, input_filename
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
