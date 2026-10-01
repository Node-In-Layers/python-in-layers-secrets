from __future__ import annotations

import os

from ..core.types import GetSecretProps, SecretsCoreContext, StoreSecretProps


class EnvSecretsServices:
    def get_stored_secret(self, props: GetSecretProps) -> str:
        value = os.environ.get(props["key"])
        if value is None:
            raise KeyError(
                f"Secret not found in process environment for key: {props['key']}"
            )
        return value

    def store_secret(self, props: StoreSecretProps) -> None:
        raise NotImplementedError("Not implemented")


def create(_context: SecretsCoreContext) -> EnvSecretsServices:
    return EnvSecretsServices()
