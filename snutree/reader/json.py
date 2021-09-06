import json
from pathlib import Path
from typing import ClassVar, Iterable


class JsonReader:

    extensions: ClassVar[list[str]] = [".json"]

    def read(self, path: Path) -> Iterable[dict[str, str]]:
        objs: object = json.loads(path.read_text())
        assert isinstance(objs, list)
        yield from objs
