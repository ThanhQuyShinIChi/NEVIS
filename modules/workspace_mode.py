"""Workspace mode (MEP / Kết cấu) logic — no Qt dependency."""
from __future__ import annotations

VALID_MODES = {"mep", "structural"}


def get_default_mode() -> str:
    return "mep"


def serialize_mode(mode: str) -> str:
    return mode if mode in VALID_MODES else get_default_mode()


def deserialize_mode(value) -> str:
    if isinstance(value, str) and value in VALID_MODES:
        return value
    return get_default_mode()


def mode_display_name(mode: str) -> str:
    return {"mep": "MEP / Đường ống", "structural": "Kết cấu"}.get(mode, mode)


# Aliases for Nevis_no_ui.py compatibility
def serialize_workspace_mode(mode: str) -> dict:
    return {"workspace_mode": serialize_mode(mode)}


def deserialize_workspace_mode(data: dict) -> str:
    if isinstance(data, dict):
        return deserialize_mode(data.get("workspace_mode"))
    return deserialize_mode(data)
