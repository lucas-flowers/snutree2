import importlib
from dataclasses import dataclass, field
from itertools import chain
from typing import ClassVar, Generic, Iterable, Protocol, TextIO, Type, TypeVar

from snutree.model.entity import CustomEntity, Entity, EntityId
from snutree.model.rank import AnyRank
from snutree.model.tree import FamilyTree, FamilyTreeConfig

M = TypeVar("M")


class Reader(Protocol):

    extensions: ClassVar[list[str]]

    def read(self, stream: TextIO) -> Iterable[dict[str, str]]:
        ...


class Parser(Protocol[AnyRank, M]):
    def parse(self, rows: Iterable[dict[str, str]]) -> Iterable[Entity[AnyRank, M]]:
        ...


class Writer(Protocol[AnyRank, M]):
    def write(self, tree: FamilyTree[AnyRank, M]) -> str:
        ...


class SnutreeApiProtocol(Protocol):
    def run(self, input_files: Iterable[tuple[TextIO, str]]) -> str:
        ...


@dataclass
class SnutreeApi(Generic[AnyRank, M]):

    rank_type: Type[AnyRank]
    readers: list[Reader]
    parser: Parser[AnyRank, M]
    tree_config: FamilyTreeConfig
    writer: Writer[AnyRank, M]

    custom_entities: list[CustomEntity[AnyRank, M]] = field(default_factory=list)
    custom_relationships: set[tuple[str, str]] = field(default_factory=set)

    @classmethod
    def from_module_name(cls, module_name: str) -> "SnutreeApi[AnyRank, M]":
        module = importlib.import_module(module_name)
        api: object = getattr(module, "__snutree__")
        assert isinstance(api, SnutreeApi)
        return api

    def run(self, input_files: Iterable[tuple[TextIO, str]]) -> str:

        readers = {extension: reader for reader in self.readers for extension in reader.extensions}

        rows = (row for input_file, extension in input_files for row in readers[extension].read(input_file))

        entities = self.parser.parse(rows)

        tree = FamilyTree(
            rank_type=self.rank_type,
            entities=chain(entities, self.custom_entities),
            relationships={(EntityId(a), EntityId(b)) for a, b in self.custom_relationships},
            config=self.tree_config,
        )

        return self.writer.write(tree)
