from csv import DictReader
from pathlib import Path
from typing import ClassVar, Iterable


class CsvReader:

    extensions: ClassVar[list[str]] = [".csv"]

    def read(self, path: Path) -> Iterable[dict[str, str]]:
        with path.open() as f:
            yield from DictReader(f)
