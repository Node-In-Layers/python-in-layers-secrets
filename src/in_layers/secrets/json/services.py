from __future__ import annotations

import json
from collections.abc import Mapping
from functools import reduce
from pathlib import Path
from typing import Any

import json5

from ..core.types import GetSecretProps, StoreSecretProps
from .types import JsonSecretsContext


def _get_by_path(data: Mapping[str, Any], path: str) -> Any:
    keys = path.split(".")

    def _step(acc: Any, key: str) -> Any:
        if acc is None:
            return None
        if isinstance(acc, Mapping) and key in acc:
            return acc[key]
        return None

    return reduce(_step, keys, data)


class JsonSecretsServices:
    def __init__(self, context: JsonSecretsContext):
        self.__context = context
        self.__file_path: Path | None = None
        self.__data: Mapping[str, Any] | None = None

    def __resolve_file_path(self) -> Path:
        if self.__file_path is not None:
            return self.__file_path
        working_directory = self.__context.constants.working_directory
        environment = self.__context.constants.environment
        basic = Path(working_directory) / f"secrets.{environment}.json"
        json5_path = Path(f"{basic}5")
        if basic.exists():
            self.__file_path = basic
            return basic
        if json5_path.exists():
            self.__file_path = json5_path
            return json5_path
        raise FileNotFoundError(f"Failed to read secrets file {basic} or {json5_path}.")

    def __load(self) -> Mapping[str, Any]:
        if self.__data is not None:
            return self.__data
        path = self.__resolve_file_path()
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as error:
            raise RuntimeError(
                f"Failed to read secrets file {path}: {error}"
            ) from error
        parsed = json5.loads(raw) if str(path).endswith("5") else json.loads(raw)
        if parsed is None or not isinstance(parsed, dict) or isinstance(parsed, list):
            raise ValueError(f"Secrets file {path} must be a JSON object")
        self.__data = parsed
        return parsed

    def get_stored_secret(self, props: GetSecretProps) -> str:
        data = self.__load()
        value = _get_by_path(data, props["key"])
        if value is None:
            raise KeyError(f"Secret not found for key: {props['key']}")
        if not isinstance(value, str):
            raise TypeError(f"Secret value for key {props['key']} is not a string")
        return value

    def get_stored_json_secret(self, props: GetSecretProps) -> Mapping[str, Any]:
        data = self.__load()
        value = _get_by_path(data, props["key"])
        if value is None:
            raise KeyError(f"Secret not found for key: {props['key']}")
        return value

    def store_secret(self, props: StoreSecretProps) -> None:
        raise NotImplementedError("Not implemented")


def create(context: JsonSecretsContext) -> JsonSecretsServices:
    return JsonSecretsServices(context)
