from __future__ import annotations

from . import services
from .services import JsonSecretsServices
from .types import JsonSecretsContext
from ..types import SecretsNamespace

name = SecretsNamespace.json.value

__all__ = [
    "JsonSecretsContext",
    "JsonSecretsServices",
    "name",
    "services",
]
