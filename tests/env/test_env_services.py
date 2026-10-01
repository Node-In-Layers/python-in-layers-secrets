from __future__ import annotations

import pytest

from in_layers.secrets.env.services import create


def test_get_stored_secret_from_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("NIL_TEST_SECRET", "secret-value")
    services = create(object())

    actual = services.get_stored_secret({"key": "NIL_TEST_SECRET"})

    assert actual == "secret-value"


def test_get_stored_secret_accepts_empty_environment_value(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("NIL_TEST_SECRET", "")
    services = create(object())

    actual = services.get_stored_secret({"key": "NIL_TEST_SECRET"})

    assert actual == ""


def test_get_stored_secret_missing_key_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NIL_TEST_SECRET", raising=False)
    services = create(object())

    with pytest.raises(KeyError, match="Secret not found in process environment"):
        services.get_stored_secret({"key": "NIL_TEST_SECRET"})


def test_store_secret_not_implemented():
    services = create(object())

    with pytest.raises(NotImplementedError, match="Not implemented"):
        services.store_secret({"key": "NIL_TEST_SECRET", "value": "value"})
