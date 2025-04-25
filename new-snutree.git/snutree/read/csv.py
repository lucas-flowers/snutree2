
from csv import DictReader

def read(fileobj, config: dict = None):
    config = config or {}
    yield from (
        {key: value or None for key, value in row.items()}
        for row in DictReader(fileobj, **config)
    )

