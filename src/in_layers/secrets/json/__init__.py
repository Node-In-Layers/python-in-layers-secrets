from __future__ import annotations

from ..types import SecretsNamespace
from . import services
from .services import JsonSecretsServices
from .types import JsonSecretsContext

name = SecretsNamespace.json.value

__all__ = [
    "JsonSecretsContext",
    "JsonSecretsServices",
    "name",
    "services",
]
