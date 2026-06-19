from __future__ import annotations

from typing import Any


VALID_WORKSPACE_MODES = {"mep", "structural"}


def get_default_mode() -> str:
    return "mep"


def normalize_workspace_mode(value: Any) -> str:
    mode = str(value or "").strip().lower()
    return mode if mode in VALID_WORKSPACE_MODES else get_default_mode()


def serialize_workspace_mode(mode: Any) -> dict[str, str]:
    return {"workspace_mode": normalize_workspace_mode(mode)}


def deserialize_workspace_mode(payload: Any) -> str:
    if not isinstance(payload, dict):
        return get_default_mode()
    return normalize_workspace_mode(payload.get("workspace_mode"))
