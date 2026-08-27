from __future__ import annotations

from collections.abc import Mapping
from functools import reduce
from typing import Any

from box import Box

from ..core.types import GetSecretProps
from ..types import SecretsNamespace
from .libs import find_nil_secret_entries
from .types import ConfigSecretsFeaturesContext, SecretFormat


def _to_get_secret_props(entry: Mapping[str, Any]) -> GetSecretProps:
    return {
        key: value
        for key, value in dict(entry).items()
        if key not in ("type", "format")
    }


def _clone_preserving_refs(value: Any) -> Any:
    """Deep-clone mappings/lists; keep modules, callables, and other objects by ref."""
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes)):
        return {k: _clone_preserving_refs(v) for k, v in dict(value).items()}
    if isinstance(value, list):
        return [_clone_preserving_refs(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_clone_preserving_refs(v) for v in value)
    return value


def _set_by_path(data: Any, path: str, value: Any) -> Any:
    keys = path.split(".")

    def _set(acc: Any, key: str, remaining: list[str], val: Any) -> Any:
        if not remaining:
            if isinstance(acc, dict):
                result = dict(acc)
                result[key] = val
                return result
            raise TypeError(f"Cannot set path on non-dict at {key}")
        next_key = remaining[0]
        child = acc.get(key) if isinstance(acc, Mapping) else None
        if child is None:
            child = {}
        new_child = _set(child, next_key, remaining[1:], val)
        if isinstance(acc, dict):
            result = dict(acc)
            result[key] = new_child
            return result
        raise TypeError(f"Cannot set path on non-dict at {key}")

    return _set(data, keys[0], keys[1:], value)


class ConfigSecretsFeatures:
    def __init__(self, context: ConfigSecretsFeaturesContext):
        self.__context = context

    def replace_secrets_config_objects(self, raw_config: Any) -> Any:
        needed = find_nil_secret_entries(raw_config)
        if not needed:
            return raw_config

        services = getattr(self.__context, "services", None)
        core = None
        if services is not None:
            core = getattr(services, SecretsNamespace.core.value, None)
            if core is None and isinstance(services, Mapping):
                core = services.get(SecretsNamespace.core.value)
        if not core:
            raise RuntimeError(
                f'Missing services["{SecretsNamespace.core.value}"]. '
                "Load secrets core (and json backend) before config globals."
            )

        def _resolve(path: str, partial: Mapping[str, Any]) -> tuple[str, Any]:
            format_value = partial.get("format") or SecretFormat.string.value
            props = _to_get_secret_props(partial)
            if format_value == SecretFormat.json.value:
                value = core.get_stored_json_secret(props)
            else:
                value = core.get_stored_secret(props)
            return path, value

        resolved = [_resolve(path, partial) for path, partial in needed.items()]

        cloned = _clone_preserving_refs(raw_config)
        updated = reduce(
            lambda acc, item: _set_by_path(acc, item[0], item[1]),
            resolved,
            cloned,
        )
        if isinstance(raw_config, Box):
            return Box(updated)
        return updated


def create(context: ConfigSecretsFeaturesContext) -> ConfigSecretsFeatures:
    return ConfigSecretsFeatures(context)
