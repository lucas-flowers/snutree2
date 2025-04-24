import importlib
import pkgutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import IO, ClassVar, Protocol, runtime_checkable

from snutree.reader.sql import SqlReaderConfig


@dataclass
class ReaderConfigs:
    sql: SqlReaderConfig | None = None


@runtime_checkable
class Reader(Protocol):
    extensions: ClassVar[list[str]]

    def read(self, stream: IO[str]) -> Iterable[dict[str, str]]: ...


def _get_reader_formats(path: Path) -> set[str]:
    input_formats: set[str] = set()
    for module_info in pkgutil.iter_modules([str(path)]):
        module = importlib.import_module(".".join([__name__, module_info.name]))
        objects: dict[str, object] = vars(module)
        for obj in objects.values():
            if isinstance(obj, Reader):
                input_formats.update(obj.extensions)
    return input_formats


INPUT_FORMATS = _get_reader_formats(Path(__file__).parent)
