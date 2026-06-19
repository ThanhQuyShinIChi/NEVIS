from __future__ import annotations

import math


Point = tuple[float, float]


def compute_scale(p1: Point, p2: Point, real_distance_mm: float) -> float:
    canvas_distance = math.hypot(float(p2[0]) - float(p1[0]), float(p2[1]) - float(p1[1]))
    real_distance = float(real_distance_mm)
    if not math.isfinite(canvas_distance) or canvas_distance <= 0.0:
        raise ValueError("Calibration points must be different")
    if not math.isfinite(real_distance) or real_distance <= 0.0:
        raise ValueError("Real distance must be positive")
    return real_distance / canvas_distance


def canvas_to_real(x: float, y: float, scale: float, origin: Point) -> Point:
    factor = float(scale)
    if not math.isfinite(factor) or factor <= 0.0:
        raise ValueError("Scale must be positive")
    return (float(x) - float(origin[0])) * factor, (float(y) - float(origin[1])) * factor


def real_to_canvas(x: float, y: float, scale: float, origin: Point) -> Point:
    factor = float(scale)
    if not math.isfinite(factor) or factor <= 0.0:
        raise ValueError("Scale must be positive")
    return float(x) / factor + float(origin[0]), float(y) / factor + float(origin[1])
