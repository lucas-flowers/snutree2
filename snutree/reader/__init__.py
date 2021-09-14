import importlib
import pkgutil
from pathlib import Path

from snutree.api import Reader


def _get_reader_formats(path: Path) -> set[str]:
    input_formats: set[str] = set()
    for module_info in pkgutil.iter_modules([str(path)]):
        module = importlib.import_module(".".join([__name__, module_info.name]))
        objects: dict[str, object] = vars(module)
        for obj in objects.values():
            if isinstance(obj, Reader):
                input_formats.update(obj.extensions)
    return input_formats


INPUT_FORMATS: set[str] = _get_reader_formats(Path(__file__).parent)
