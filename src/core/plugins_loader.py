import importlib
import logging
import pkgutil
from typing import List

from plugins.base import Plugin

log = logging.getLogger("it_tester.plugins")


def load_plugins() -> List[Plugin]:
    plugins: List[Plugin] = []

    try:
        import plugins as plugins_pkg  # type: ignore
    except ImportError:
        log.warning("plugins package not found on sys.path")
        return plugins

    pkg_path = getattr(plugins_pkg, "__path__", None)
    if not pkg_path:
        log.warning("plugins package missing __path__ attribute")
        return plugins

    for module_info in pkgutil.iter_modules(pkg_path):
        name = module_info.name
        if name in {"base", "__init__"}:
            continue
        full_name = f"plugins.{name}"
        try:
            module = importlib.import_module(full_name)
            get_plugin = getattr(module, "get_plugin", None)
            if callable(get_plugin):
                plugin = get_plugin()
                if isinstance(plugin, Plugin):
                    plugins.append(plugin)
                    log.info("Plugin loaded: %s", full_name)
        except Exception as exc:
            log.warning("Plugin load failed (%s): %s", full_name, exc)
    return plugins
