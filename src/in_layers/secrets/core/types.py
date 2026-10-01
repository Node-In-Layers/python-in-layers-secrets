from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Protocol, TypedDict

from in_layers.core.protocols import CommonContext, Config


class GetSecretProps(TypedDict, total=False):
    """Props for retrieving a stored secret."""

    key: str


class StoreSecretProps(TypedDict, total=False):
    """Props for storing a string secret."""

    key: str
    value: str


class StoreSecretJsonProps(TypedDict, total=False):
    """Props for storing a JSON secret."""

    key: str
    value: Mapping[str, Any]


class SecretsService(Protocol):
    """
    What a backend secrets manager implements.
    JSON methods are optional; core fills them in when missing.
    """

    def get_stored_secret(self, props: GetSecretProps) -> str: ...

    def store_secret(self, props: StoreSecretProps) -> None: ...

    def get_stored_json_secret(self, props: GetSecretProps) -> Mapping[str, Any]: ...

    def store_secret_json(self, props: StoreSecretJsonProps) -> None: ...


SECRETS_CONFIG_RESOLUTION = (
    "secret_service_factory",
    "json_backend_default",
    "env_backend_default",
    "dotenv_backend_default",
)


class SecretsConfig(TypedDict, total=False):
    """
    Configuration under SecretsNamespace.core.

    Backend resolution follows SECRETS_CONFIG_RESOLUTION: use
    secret_service_factory if set, otherwise the json file backend.
    """

    secret_service_factory: Callable[[CommonContext], Any]
    dotenv_file_path: str


class WithSecretsConfig(Config, Protocol):
    in_layers_secrets: SecretsConfig


class SecretsCoreContext(Protocol):
    config: WithSecretsConfig
    root_logger: Any
    constants: Any
