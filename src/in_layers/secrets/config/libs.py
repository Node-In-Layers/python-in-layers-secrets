from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import reduce
from typing import Any

from .types import (
    NIL_SECRET_ENTRY_KEY,
    NIL_SECRET_ENTRY_TYPE,
    NilSecretsToReplace,
)


def is_plain_object(obj: Any) -> bool:
    return isinstance(obj, dict) and not isinstance(obj, list)


def _find_objects(
    path: str | None,
    obj: Any,
    is_match: Callable[[object], bool],
) -> list[str]:
    if not is_plain_object(obj):
        return []
    if is_match(obj):
        if not path:
            raise ValueError("Cannot match base object")
        return [path]
    return reduce(
        lambda acc, item: acc
        + _find_objects(
            f"{path}.{item[0]}" if path else item[0],
            item[1],
            is_match,
        ),
        list(obj.items()),
        [],
    )


def find_nested_objects(obj: Any, is_match: Callable[[object], bool]) -> list[str]:
    return _find_objects(None, obj, is_match)


def is_nil_secret_entry(obj: object) -> bool:
    if not isinstance(obj, Mapping):
        return False
    return (
        NIL_SECRET_ENTRY_KEY in obj
        and obj[NIL_SECRET_ENTRY_KEY] == NIL_SECRET_ENTRY_TYPE
        and "key" in obj
    )


def _get_by_path(data: Any, path: str) -> Any:
    return reduce(
        lambda acc, key: (
            acc[key] if isinstance(acc, Mapping) and key in acc else None
        ),
        path.split("."),
        data,
    )


def find_nil_secret_entries(raw_config: object) -> NilSecretsToReplace:
    paths = find_nested_objects(raw_config, is_nil_secret_entry)
    return reduce(
        lambda acc, path: {**acc, path: _get_by_path(raw_config, path)},
        paths,
        {},
    )
