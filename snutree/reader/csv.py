from csv import DictReader
from pathlib import Path
from typing import Iterable


class CsvReader:
    def read(self, path: Path) -> Iterable[dict[str, str]]:
        with path.open() as f:
            yield from DictReader(f)
