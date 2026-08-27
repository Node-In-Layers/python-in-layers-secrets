from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from box import Box

from in_layers.core.protocols import CommonContext

from ..json import services as json_services
from ..types import SecretsNamespace
from .types import (
    GetSecretProps,
    SecretsConfig,
    SecretsCoreContext,
    StoreSecretJsonProps,
    StoreSecretProps,
)


class _JsonDefaultsSecretsService:
    """Wraps a backend and fills in missing JSON methods."""

    def __init__(self, base: Any):
        self.__base = base

    def get_stored_secret(self, props: GetSecretProps) -> str:
        return self.__base.get_stored_secret(props)

    def store_secret(self, props: StoreSecretProps) -> None:
        store = getattr(self.__base, "store_secret", None)
        if store is None:
            raise NotImplementedError("Not implemented")
        store(props)

    def store_secret_json(self, props: StoreSecretJsonProps) -> None:
        native = getattr(self.__base, "store_secret_json", None)
        if native is not None:
            native(props)
            return
        as_string = json.dumps(props["value"])
        self.store_secret({**dict(props), "value": as_string})

    def get_stored_json_secret(self, props: GetSecretProps) -> Mapping[str, Any]:
        native = getattr(self.__base, "get_stored_json_secret", None)
        if native is not None:
            return native(props)
        as_string = self.get_stored_secret(props)
        return json.loads(as_string)


def merge_json_defaults(base: Any) -> _JsonDefaultsSecretsService:
    return _JsonDefaultsSecretsService(base)


def _resolve_raw_secrets_service(
    secrets_config: SecretsConfig | Mapping[str, Any],
    common_globals: CommonContext,
    context: SecretsCoreContext,
) -> Any:
    factory = None
    if isinstance(secrets_config, Mapping):
        factory = secrets_config.get("secret_service_factory")
    else:
        factory = getattr(secrets_config, "secret_service_factory", None)
    if factory is not None:
        return factory(common_globals)
    return json_services.create(context)


class SecretsCoreServices:
    def __init__(self, context: SecretsCoreContext):
        self.__context = context
        self.__backend: _JsonDefaultsSecretsService | None = None

        secrets_config = getattr(context.config, SecretsNamespace.core.value, None)
        if secrets_config is None and isinstance(context.config, Mapping):
            secrets_config = context.config.get(SecretsNamespace.core.value)
        if secrets_config is None:
            raise ValueError(f'config["{SecretsNamespace.core.value}"] is required')

        self.__secrets_config = secrets_config
        self.__common_globals: CommonContext = Box(
            {
                "config": context.config,
                "root_logger": context.root_logger,
                "constants": context.constants,
            }
        )

    def __resolve_backend(self) -> _JsonDefaultsSecretsService:
        if self.__backend is None:
            raw = _resolve_raw_secrets_service(
                self.__secrets_config,
                self.__common_globals,
                self.__context,
            )
            self.__backend = merge_json_defaults(raw)
        return self.__backend

    def get_stored_secret(self, props: GetSecretProps) -> str:
        return self.__resolve_backend().get_stored_secret(props)

    def get_stored_json_secret(self, props: GetSecretProps) -> Mapping[str, Any]:
        return self.__resolve_backend().get_stored_json_secret(props)

    def store_secret(self, props: StoreSecretProps) -> None:
        return self.__resolve_backend().store_secret(props)

    def store_secret_json(self, props: StoreSecretJsonProps) -> None:
        return self.__resolve_backend().store_secret_json(props)


def create(context: SecretsCoreContext) -> SecretsCoreServices:
    return SecretsCoreServices(context)
