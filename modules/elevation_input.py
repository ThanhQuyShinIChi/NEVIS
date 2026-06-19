from __future__ import annotations

import math


NODE_Z_MIN_MM = -50000.0
NODE_Z_MAX_MM = 200000.0


def validate_node_z_input(raw: str) -> tuple[float | None, str]:
    text = str(raw or "").strip()
    if not text:
        return None, ""

    try:
        value = float(text)
    except (TypeError, ValueError):
        return None, "Node Z must be a number or blank."

    if not math.isfinite(value) or not NODE_Z_MIN_MM <= value <= NODE_Z_MAX_MM:
        return None, "Node Z must be between -50000 and 200000 mm."
    return value, ""
