from __future__ import annotations

from box import Box

from in_layers.secrets import SecretsNamespace
from in_layers.secrets.config.features import create


def test_replace_noop_when_empty():
    context = Box(config=Box({}), services=Box({}))
    features = create(context)
    raw = {"a": 1}
    assert features.replace_secrets_config_objects(raw) is raw


def test_replace_string_and_json():
    class Core:
        def get_stored_secret(self, props):
            assert props["key"] == "/s"
            assert props.get("aws_service") == "secretsManager"
            return "the-secret"

        def get_stored_json_secret(self, props):
            assert props["key"] == "/j"
            return {"n": 1}

    context = Box(
        config=Box({}),
        services=Box({SecretsNamespace.core.value: Core()}),
    )
    features = create(context)
    raw = {
        "your_domain": {
            "my_secret_key": {
                "type": "nil-secret",
                "format": "string",
                "key": "/s",
                "aws_service": "secretsManager",
            }
        },
        "another": {
            "nested": {
                "another_secret_key": {
                    "type": "nil-secret",
                    "format": "json",
                    "key": "/j",
                }
            }
        },
    }
    actual = features.replace_secrets_config_objects(raw)
    assert actual["your_domain"]["my_secret_key"] == "the-secret"
    assert actual["another"]["nested"]["another_secret_key"] == {"n": 1}


def test_replace_missing_core_raises():
    context = Box(config=Box({}), services=Box({}))
    features = create(context)
    raw = {
        "x": {"type": "nil-secret", "key": "/k"},
    }
    try:
        features.replace_secrets_config_objects(raw)
        raised = False
    except RuntimeError:
        raised = True
    assert raised is True
