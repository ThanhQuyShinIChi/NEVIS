from __future__ import annotations

from modules.workspace_mode import (
    deserialize_workspace_mode,
    get_default_mode,
    normalize_workspace_mode,
    serialize_workspace_mode,
)


def test_get_default_mode_is_mep() -> None:
    assert get_default_mode() == "mep"


def test_workspace_mode_round_trip() -> None:
    for mode in ("mep", "structural"):
        assert deserialize_workspace_mode(serialize_workspace_mode(mode)) == mode


def test_legacy_or_invalid_payload_uses_mep() -> None:
    assert deserialize_workspace_mode({}) == "mep"
    assert deserialize_workspace_mode(None) == "mep"
    assert deserialize_workspace_mode({"workspace_mode": "unknown"}) == "mep"
    assert normalize_workspace_mode(" STRUCTURAL ") == "structural"
