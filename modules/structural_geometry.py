"""Geometry helpers for structural element drawing — no Qt dependency."""
from __future__ import annotations
import math


def rect_from_two_points(p1: tuple, p2: tuple) -> list:
    """Return 4-corner rectangle [(x0,y0),(x1,y0),(x1,y1),(x0,y1)] from two diagonal points."""
    x0, y0 = min(p1[0], p2[0]), min(p1[1], p2[1])
    x1, y1 = max(p1[0], p2[0]), max(p1[1], p2[1])
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def snap_to_grid(x: float, y: float, grid_mm: float) -> tuple:
    """Snap point to nearest grid intersection."""
    if grid_mm <= 0:
        return (x, y)
    return (round(x / grid_mm) * grid_mm, round(y / grid_mm) * grid_mm)


def nearest_snap_point(x: float, y: float, candidates: list, tolerance: float) -> tuple | None:
    """Return nearest candidate point within tolerance, or None."""
    best = None
    best_d = tolerance
    for pt in candidates:
        d = math.hypot(pt[0] - x, pt[1] - y)
        if d <= best_d:
            best_d = d
            best = pt
    return best


def rect_from_center_wl(cx: float, cy: float, w: float, l: float) -> list:
    """Return 4-corner rectangle centered at (cx, cy) with width w and length l."""
    hw, hl = w / 2.0, l / 2.0
    return [(cx - hw, cy - hl), (cx + hw, cy - hl), (cx + hw, cy + hl), (cx - hw, cy + hl)]


def rect_bounds(points: list) -> tuple:
    """Return (x0, y0, x1, y1) bounding box of a polygon."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def rect_contains(outer: list, inner: list) -> bool:
    """Return True if inner bounding box is fully inside outer bounding box."""
    ox0, oy0, ox1, oy1 = rect_bounds(outer)
    ix0, iy0, ix1, iy1 = rect_bounds(inner)
    return ix0 >= ox0 and iy0 >= oy0 and ix1 <= ox1 and iy1 <= oy1


def grid_points_in_view(x0: float, y0: float, x1: float, y1: float,
                         grid_mm: float, max_points: int = 2000) -> list:
    """Return grid intersection points visible in (x0,y0)-(x1,y1) view rectangle."""
    if grid_mm <= 0:
        return []
    import math as _math
    col_start = int(_math.floor(x0 / grid_mm))
    col_end = int(_math.ceil(x1 / grid_mm))
    row_start = int(_math.floor(y0 / grid_mm))
    row_end = int(_math.ceil(y1 / grid_mm))
    pts = []
    for col in range(col_start, col_end + 1):
        for row in range(row_start, row_end + 1):
            pts.append((col * grid_mm, row * grid_mm))
            if len(pts) >= max_points:
                return pts
    return pts
