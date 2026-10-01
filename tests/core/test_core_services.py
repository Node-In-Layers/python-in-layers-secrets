from __future__ import annotations

import json
from pathlib import Path

from box import Box

from in_layers.secrets import SecretsNamespace
from in_layers.secrets.core.services import create


def test_missing_core_config_raises():
    context = Box(
        config=Box({}),
        root_logger={},
        constants=Box(working_directory=".", environment="test"),
    )
    try:
        create(context)
        raised = False
    except ValueError:
        raised = True
    assert raised is True


def test_factory_backend_and_json_defaults():
    calls = {"count": 0}

    class StubBackend:
        def get_stored_secret(self, props):
            calls["count"] += 1
            return json.dumps({"hello": "world"}) if props["key"] == "json" else "plain"

        def store_secret(self, props):
            self.last = props

    def factory(_ctx):
        return StubBackend()

    context = Box(
        config=Box({SecretsNamespace.core.value: Box(secret_service_factory=factory)}),
        root_logger={},
        constants=Box(working_directory=".", environment="test"),
    )
    services = create(context)
    assert services.get_stored_secret({"key": "plain"}) == "plain"
    assert services.get_stored_json_secret({"key": "json"}) == {"hello": "world"}
    services.store_secret_json({"key": "x", "value": {"a": 1}})
    assert calls["count"] == 2


def test_default_json_backend(tmp_path: Path):
    secrets_file = tmp_path / "secrets.test.json"
    secrets_file.write_text(json.dumps({"api_key": "secret-1"}), encoding="utf-8")
    context = Box(
        config=Box({SecretsNamespace.core.value: Box({})}),
        root_logger={},
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    assert services.get_stored_secret({"key": "api_key"}) == "secret-1"


def test_default_environment_backend_after_json_misses(monkeypatch):
    monkeypatch.setenv("NIL_TEST_SECRET", "environment-secret")
    context = Box(
        config=Box({SecretsNamespace.core.value: Box({})}),
        root_logger={},
        constants=Box(working_directory="/tmp", environment="test"),
    )
    services = create(context)

    assert services.get_stored_secret({"key": "NIL_TEST_SECRET"}) == (
        "environment-secret"
    )


def test_default_dotenv_backend_after_json_and_environment_misses(tmp_path: Path):
    (tmp_path / ".env").write_text(
        "NIL_TEST_SECRET=dotenv-secret\n",
        encoding="utf-8",
    )
    context = Box(
        config=Box({SecretsNamespace.core.value: Box({})}),
        root_logger={},
        constants=Box(working_directory=str(tmp_path), environment="test"),
    )
    services = create(context)

    assert services.get_stored_secret({"key": "NIL_TEST_SECRET"}) == "dotenv-secret"
