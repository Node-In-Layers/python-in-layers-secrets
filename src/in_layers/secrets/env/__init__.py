from __future__ import annotations

from ..types import SecretsNamespace
from . import services
from .services import EnvSecretsServices

name = SecretsNamespace.env.value

__all__ = [
    "EnvSecretsServices",
    "name",
    "services",
]
