from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Protocol, TypedDict

from in_layers.core.protocols import Config

NIL_SECRET_ENTRY_KEY = "type"  # noqa: S105
NIL_SECRET_ENTRY_TYPE = "nil-secret"  # noqa: S105


class SecretFormat(StrEnum):
    string = "string"
    json = "json"


class NilSecretEntry(TypedDict, total=False):
    """Shape of a config placeholder replaced at globals time."""

    type: str
    format: str
    key: str


NilSecretsToReplace = Mapping[str, NilSecretEntry]


class ConfigSecretsFeaturesContext(Protocol):
    config: Config
    services: Any
