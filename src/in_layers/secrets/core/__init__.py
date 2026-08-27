from __future__ import annotations

from ..types import SecretsNamespace
from . import services
from .services import SecretsCoreServices
from .types import (
    SECRETS_CONFIG_RESOLUTION,
    GetSecretProps,
    SecretsConfig,
    SecretsCoreContext,
    SecretsService,
    StoreSecretJsonProps,
    StoreSecretProps,
    WithSecretsConfig,
)

name = SecretsNamespace.core.value

__all__ = [
    "SECRETS_CONFIG_RESOLUTION",
    "GetSecretProps",
    "SecretsConfig",
    "SecretsCoreContext",
    "SecretsCoreServices",
    "SecretsService",
    "StoreSecretJsonProps",
    "StoreSecretProps",
    "WithSecretsConfig",
    "name",
    "services",
]
