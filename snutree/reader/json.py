import json
from typing import ClassVar, Iterable, TextIO


class JsonReader:

    extensions: ClassVar[list[str]] = [".json"]

    def read(self, stream: TextIO) -> Iterable[dict[str, str]]:
        objs: object = json.load(stream)
        assert isinstance(objs, list)
        yield from objs
