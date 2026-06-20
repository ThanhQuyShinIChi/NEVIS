"""Tests for modules/workspace_mode.py — no Qt dependency."""
import pytest
from modules.workspace_mode import (
    get_default_mode, serialize_mode, deserialize_mode, mode_display_name,
)


def test_default_mode_is_mep():
    assert get_default_mode() == "mep"

def test_serialize_mep():
    assert serialize_mode("mep") == "mep"

def test_serialize_structural():
    assert serialize_mode("structural") == "structural"

def test_serialize_invalid_falls_back():
    assert serialize_mode("unknown") == "mep"

def test_deserialize_valid():
    assert deserialize_mode("structural") == "structural"

def test_deserialize_invalid():
    assert deserialize_mode("anything") == "mep"

def test_deserialize_none():
    assert deserialize_mode(None) == "mep"

def test_deserialize_number():
    assert deserialize_mode(42) == "mep"

def test_display_name_mep():
    assert "MEP" in mode_display_name("mep")

def test_display_name_structural():
    name = mode_display_name("structural")
    assert "Kết cấu" in name or "structural" in name.lower()
