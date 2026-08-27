from __future__ import annotations

from box import Box

from in_layers.secrets.config.libs import (
    find_nested_objects,
    find_nil_secret_entries,
    is_nil_secret_entry,
)


def test_is_nil_secret_entry_true():
    input_obj = {"type": "nil-secret", "key": "/a/b"}
    assert is_nil_secret_entry(input_obj) is True


def test_is_nil_secret_entry_false_without_key():
    input_obj = {"type": "nil-secret"}
    assert is_nil_secret_entry(input_obj) is False


def test_find_nested_objects_paths():
    input_obj = {
        "a": {"type": "nil-secret", "key": "x"},
        "b": {"nested": {"type": "nil-secret", "key": "y"}},
    }
    actual = find_nested_objects(input_obj, is_nil_secret_entry)
    expected = ["a", "b.nested"]
    assert sorted(actual) == sorted(expected)


def test_find_nested_objects_root_match_raises():
    input_obj = {"type": "nil-secret", "key": "x"}
    try:
        find_nested_objects(input_obj, is_nil_secret_entry)
        raised = False
    except ValueError:
        raised = True
    assert raised is True


def test_find_nil_secret_entries():
    input_obj = {
        "a": {"type": "nil-secret", "key": "x", "format": "string"},
        "b": {"c": {"type": "nil-secret", "key": "y", "format": "json"}},
    }
    actual = find_nil_secret_entries(input_obj)
    assert actual["a"]["key"] == "x"
    assert actual["b.c"]["key"] == "y"
