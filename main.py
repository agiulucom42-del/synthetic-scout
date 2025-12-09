import importlib
import logging
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

try:
    from core import runner
except ImportError:
    sys.path.append(str(SRC))
    from core import runner  # type: ignore  # fallback for misconfigured environments


def _import_all_tests() -> None:
    tests_pkg_path = ROOT / "tests"
    if not tests_pkg_path.exists():
        logging.warning("Tests directory not found at %s", tests_pkg_path)
        return

    for module in pkgutil.iter_modules([str(tests_pkg_path)]):
        full_name = f"tests.{module.name}"
        importlib.import_module(full_name)


if __name__ == "__main__":
    _import_all_tests()
    raise SystemExit(runner.main(sys.argv))
