"""Scale calibration: compute canvas-to-real-world scale — no Qt dependency."""
from __future__ import annotations
import math


def compute_scale(p1: tuple, p2: tuple, real_distance_mm: float) -> float:
    """Return scale = real_distance_mm / canvas_distance. Raises ValueError if distance is zero."""
    canvas_d = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    if canvas_d == 0:
        raise ValueError("Canvas distance is zero — pick two different points")
    if real_distance_mm <= 0:
        raise ValueError("Real distance must be > 0")
    return real_distance_mm / canvas_d


def canvas_to_real(x: float, y: float, scale: float, origin: tuple = (0.0, 0.0)) -> tuple:
    """Convert canvas coordinates to real-world mm."""
    return ((x - origin[0]) * scale, (y - origin[1]) * scale)


def real_to_canvas(x: float, y: float, scale: float, origin: tuple = (0.0, 0.0)) -> tuple:
    """Convert real-world mm to canvas coordinates."""
    if scale == 0:
        raise ValueError("Scale cannot be zero")
    return (x / scale + origin[0], y / scale + origin[1])


def format_scale_ratio(scale: float) -> str:
    """Return human-readable scale string like '1:50'."""
    if scale <= 0:
        return "N/A"
    ratio = round(scale)
    return "1:{}".format(ratio)
