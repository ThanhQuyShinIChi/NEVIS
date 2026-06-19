from __future__ import annotations

import math
from collections.abc import Iterable


Point = tuple[float, float]


def rect_from_two_points(p1: Point, p2: Point) -> list[Point]:
    """Return an axis-aligned rectangle in clockwise screen order."""
    left, right = sorted((float(p1[0]), float(p2[0])))
    top, bottom = sorted((float(p1[1]), float(p2[1])))
    return [(left, top), (right, top), (right, bottom), (left, bottom)]


def snap_to_grid(x: float, y: float, grid_mm: float) -> Point:
    grid = float(grid_mm)
    if not math.isfinite(grid) or grid <= 0.0:
        return float(x), float(y)

    def snap(value: float) -> float:
        units = float(value) / grid
        rounded = math.floor(units + 0.5) if units >= 0.0 else math.ceil(units - 0.5)
        return rounded * grid

    return snap(x), snap(y)


def nearest_snap_point(
    x: float,
    y: float,
    candidates: Iterable[Point],
    tolerance: float,
) -> Point | None:
    tolerance = max(0.0, float(tolerance))
    nearest: Point | None = None
    nearest_distance = tolerance
    for candidate in candidates:
        point = float(candidate[0]), float(candidate[1])
        distance = math.hypot(point[0] - float(x), point[1] - float(y))
        if distance <= tolerance and (nearest is None or distance < nearest_distance):
            nearest = point
            nearest_distance = distance
    return nearest
