from __future__ import annotations

import math
from typing import Any

from modules.structural_geometry import Point


MAX_STRUCTURAL_DIMENSION_MM = 99999.0


def validate_dimension(value: Any, name: str) -> tuple[float, str]:
    label = str(name or "Kích thước").strip()
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0, f"{label} phải là một số."
    if not math.isfinite(number):
        return number, f"{label} phải là một số hữu hạn."
    if number > MAX_STRUCTURAL_DIMENSION_MM:
        return number, f"{label} không được vượt quá {MAX_STRUCTURAL_DIMENSION_MM:g} mm."
    if label.upper() == "C":
        if number < 0.0:
            return number, "C phải lớn hơn hoặc bằng 0."
    elif number <= 0.0:
        return number, f"{label} phải lớn hơn 0."
    return number, ""


def rect_from_center_wl(cx: float, cy: float, width: float, length: float) -> list[Point]:
    half_width = float(width) / 2.0
    half_length = float(length) / 2.0
    center_x, center_y = float(cx), float(cy)
    return [
        (center_x - half_width, center_y - half_length),
        (center_x + half_width, center_y - half_length),
        (center_x + half_width, center_y + half_length),
        (center_x - half_width, center_y + half_length),
    ]
