import json
from typing import IO, ClassVar, Iterable


class JsonReader:

    extensions: ClassVar[list[str]] = [".json"]

    def read(self, stream: IO[str]) -> Iterable[dict[str, str]]:
        objs: object = json.load(stream)
        assert isinstance(objs, list)
        yield from objs
