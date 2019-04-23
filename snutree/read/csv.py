
from csv import DictReader

def read(fileobj, config: dict = None):
    config = config or {}
    yield from DictReader(fileobj, **config)

