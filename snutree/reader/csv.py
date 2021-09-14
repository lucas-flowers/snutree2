from csv import DictReader
from typing import IO, ClassVar, Iterable


class CsvReader:

    extensions: ClassVar[list[str]] = [".csv"]

    def read(self, stream: IO[str]) -> Iterable[dict[str, str]]:
        yield from DictReader(stream)
