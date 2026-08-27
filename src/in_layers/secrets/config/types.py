from __future__ import annotations

from enum import Enum
from typing import Any, Mapping, Protocol, TypedDict

from in_layers.core.protocols import Config

NIL_SECRET_ENTRY_KEY = "type"
NIL_SECRET_ENTRY_TYPE = "nil-secret"


class SecretFormat(str, Enum):
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
