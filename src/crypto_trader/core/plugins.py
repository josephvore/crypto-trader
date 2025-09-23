from __future__ import annotations

import importlib
from typing import Any, cast


def load_class(dotted_path: str) -> type[Any]:
    if ":" in dotted_path:
        mod_path, cls_name = dotted_path.split(":", 1)
    else:
        parts = dotted_path.split(".")
        mod_path, cls_name = ".".join(parts[:-1]), parts[-1]
    module = importlib.import_module(mod_path)
    return cast(type[Any], getattr(module, cls_name))


def build_from_path(dotted_path: str, params: dict[str, Any] | None = None) -> Any:
    cls = load_class(dotted_path)
    return cls(**(params or {}))
