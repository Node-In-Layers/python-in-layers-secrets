from __future__ import annotations

from enum import StrEnum


class SecretsNamespace(StrEnum):
    core = "in_layers_secrets"
    json = "in_layers_secrets_json"
    config = "in_layers_secrets_config"
    env = "in_layers_secrets_env"
    dotenv = "in_layers_secrets_dotenv"
