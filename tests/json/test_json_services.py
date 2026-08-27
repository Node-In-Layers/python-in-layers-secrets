from __future__ import annotations

import json
from pathlib import Path

from box import Box

from in_layers.secrets.json.services import create


def test_get_stored_secret_from_json(tmp_path: Path):
    secrets_file = tmp_path / "secrets.test.json"
    secrets_file.write_text(
        json.dumps({"plain": "value-1", "nested": {"key": "value-2"}}),
        encoding="utf-8",
    )
    context = Box(
        config=Box({}),
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    assert services.get_stored_secret({"key": "plain"}) == "value-1"
    assert services.get_stored_secret({"key": "nested.key"}) == "value-2"


def test_get_stored_json_secret_from_json(tmp_path: Path):
    secrets_file = tmp_path / "secrets.test.json"
    secrets_file.write_text(
        json.dumps({"obj": {"a": 1, "b": "two"}}),
        encoding="utf-8",
    )
    context = Box(
        config=Box({}),
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    actual = services.get_stored_json_secret({"key": "obj"})
    assert actual == {"a": 1, "b": "two"}


def test_get_stored_secret_json5(tmp_path: Path):
    secrets_file = tmp_path / "secrets.test.json5"
    secrets_file.write_text("{ plain: 'value-json5' }", encoding="utf-8")
    context = Box(
        config=Box({}),
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    assert services.get_stored_secret({"key": "plain"}) == "value-json5"


def test_missing_key_raises(tmp_path: Path):
    secrets_file = tmp_path / "secrets.test.json"
    secrets_file.write_text(json.dumps({"plain": "value-1"}), encoding="utf-8")
    context = Box(
        config=Box({}),
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    try:
        services.get_stored_secret({"key": "missing"})
        raised = False
    except KeyError:
        raised = True
    assert raised is True


def test_non_string_raises(tmp_path: Path):
    secrets_file = tmp_path / "secrets.test.json"
    secrets_file.write_text(json.dumps({"plain": 123}), encoding="utf-8")
    context = Box(
        config=Box({}),
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    try:
        services.get_stored_secret({"key": "plain"})
        raised = False
    except TypeError:
        raised = True
    assert raised is True


def test_store_secret_not_implemented(tmp_path: Path):
    secrets_file = tmp_path / "secrets.test.json"
    secrets_file.write_text(json.dumps({"plain": "value-1"}), encoding="utf-8")
    context = Box(
        config=Box({}),
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    try:
        services.store_secret({"key": "plain", "value": "x"})
        raised = False
    except NotImplementedError:
        raised = True
    assert raised is True


def test_missing_file_raises(tmp_path: Path):
    context = Box(
        config=Box({}),
        constants=Box(
            working_directory=str(tmp_path),
            environment="test",
        ),
    )
    services = create(context)
    try:
        services.get_stored_secret({"key": "plain"})
        raised = False
    except FileNotFoundError:
        raised = True
    assert raised is True
