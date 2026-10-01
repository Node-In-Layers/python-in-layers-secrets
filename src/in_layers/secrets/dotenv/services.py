from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values

from ..core.types import GetSecretProps, SecretsCoreContext, StoreSecretProps


class DotenvSecretsServices:
    def __init__(self, context: SecretsCoreContext):
        self.__context = context
        self.__data: dict[str, str] | None = None

    def __load(self) -> dict[str, str]:
        if self.__data is not None:
            return self.__data

        config = getattr(self.__context, "config", {})
        secrets_config = (
            config.get("in_layers_secrets", {})
            if isinstance(config, dict)
            else getattr(config, "in_layers_secrets", {})
        )
        configured_path = (
            secrets_config.get("dotenv_file_path", ".env")
            if isinstance(secrets_config, dict)
            else getattr(secrets_config, "dotenv_file_path", ".env")
        )
        working_directory = self.__context.constants.working_directory
        path = Path(configured_path)
        file_path = path if path.is_absolute() else Path(working_directory) / path
        if not file_path.exists():
            raise FileNotFoundError(f"Failed to read dotenv file {file_path}.")

        values = dotenv_values(file_path)
        self.__data = {key: value for key, value in values.items() if value is not None}
        return self.__data

    def get_stored_secret(self, props: GetSecretProps) -> str:
        value = self.__load().get(props["key"])
        if value is None:
            raise KeyError(f"Secret not found in dotenv file for key: {props['key']}")
        return value

    def store_secret(self, props: StoreSecretProps) -> None:
        raise NotImplementedError("Not implemented")


def create(context: SecretsCoreContext) -> DotenvSecretsServices:
    return DotenvSecretsServices(context)
