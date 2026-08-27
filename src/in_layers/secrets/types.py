from __future__ import annotations

from enum import Enum


class SecretsNamespace(str, Enum):
    core = "in_layers_secrets"
    json = "in_layers_secrets_json"
    config = "in_layers_secrets_config"
