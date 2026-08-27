from __future__ import annotations

from in_layers.secrets import SECRETS_CONFIG_RESOLUTION, SecretFormat, SecretsNamespace
from in_layers.secrets.config.types import NIL_SECRET_ENTRY_TYPE


def test_namespace_values():
    assert SecretsNamespace.core.value == "in_layers_secrets"
    assert SecretsNamespace.json.value == "in_layers_secrets_json"
    assert SecretsNamespace.config.value == "in_layers_secrets_config"


def test_secret_format_values():
    assert SecretFormat.string.value == "string"
    assert SecretFormat.json.value == "json"


def test_resolution_steps():
    assert SECRETS_CONFIG_RESOLUTION == (
        "secret_service_factory",
        "json_backend_default",
    )


def test_nil_secret_type_constant():
    assert NIL_SECRET_ENTRY_TYPE == "nil-secret"
