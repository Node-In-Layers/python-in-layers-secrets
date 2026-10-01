from __future__ import annotations

from ..types import SecretsNamespace
from . import services
from .services import DotenvSecretsServices

name = SecretsNamespace.dotenv.value

__all__ = [
    "DotenvSecretsServices",
    "name",
    "services",
]
