from __future__ import annotations

from pathlib import Path

import pytest
from box import Box

from in_layers.secrets.dotenv.services import create


def _context(directory: Path, config: Box | None = None) -> Box:
    return Box(
        config=config or Box({}),
        constants=Box(working_directory=str(directory), environment="test"),
    )


def test_get_stored_secret_from_default_dotenv_file(tmp_path: Path):
    (tmp_path / ".env").write_text("NIL_TEST_SECRET=secret-value\n", encoding="utf-8")
    services = create(_context(tmp_path))

    actual = services.get_stored_secret({"key": "NIL_TEST_SECRET"})

    assert actual == "secret-value"


def test_get_stored_secret_from_configured_dotenv_file(tmp_path: Path):
    (tmp_path / "local.env").write_text(
        "NIL_TEST_SECRET=secret-value\n",
        encoding="utf-8",
    )
    config = Box(in_layers_secrets=Box(dotenv_file_path="local.env"))
    services = create(_context(tmp_path, config))

    actual = services.get_stored_secret({"key": "NIL_TEST_SECRET"})

    assert actual == "secret-value"


def test_get_stored_secret_missing_key_raises(tmp_path: Path):
    (tmp_path / ".env").write_text("NIL_OTHER_SECRET=value\n", encoding="utf-8")
    services = create(_context(tmp_path))

    with pytest.raises(KeyError, match="Secret not found in dotenv file"):
        services.get_stored_secret({"key": "NIL_TEST_SECRET"})


def test_store_secret_not_implemented(tmp_path: Path):
    services = create(_context(tmp_path))

    with pytest.raises(NotImplementedError, match="Not implemented"):
        services.store_secret({"key": "NIL_TEST_SECRET", "value": "value"})
