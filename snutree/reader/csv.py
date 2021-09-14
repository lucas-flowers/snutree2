from csv import DictReader
from typing import ClassVar, Iterable, TextIO


class CsvReader:

    extensions: ClassVar[list[str]] = [".csv"]

    def read(self, stream: TextIO) -> Iterable[dict[str, str]]:
        yield from DictReader(stream)
