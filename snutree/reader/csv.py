from collections.abc import Iterable
from csv import DictReader
from typing import IO, ClassVar


class CsvReader:
    extensions: ClassVar[list[str]] = [".csv"]

    def read(self, stream: IO[str]) -> Iterable[dict[str, str]]:
        yield from DictReader(stream)
