from __future__ import annotations

from .types import ConfigSecretsFeaturesContext


class ConfigSecretsServices:
    def __init__(self, context: ConfigSecretsFeaturesContext):
        self.__context = context


def create(context: ConfigSecretsFeaturesContext) -> ConfigSecretsServices:
    return ConfigSecretsServices(context)
