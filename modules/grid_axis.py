"""Grid axis (通り芯 Toori-shin) data model — no Qt dependency."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class GridAxis:
    name: str        # "X1", "X2", "Y1", "Y2"...
    direction: str   # "X" (vertical line) or "Y" (horizontal line)
    position: float  # canvas coordinate (mm)


def grid_axis_to_dict(a: GridAxis) -> dict:
    return {"name": a.name, "direction": a.direction, "position": a.position}


def grid_axis_from_dict(d: dict) -> GridAxis:
    name = str(d.get("name", ""))
    direction = str(d.get("direction", "X"))
    if direction not in ("X", "Y"):
        direction = "X"
    try:
        position = float(d.get("position", 0.0))
    except (TypeError, ValueError):
        position = 0.0
    return GridAxis(name=name, direction=direction, position=position)


def build_axis_intersections(x_axes: list, y_axes: list) -> list:
    """Return list of (x, y) intersection points between X-axes and Y-axes."""
    pts = []
    for xa in x_axes:
        for ya in y_axes:
            pts.append((xa.position, ya.position))
    return pts


def find_nearest_axis_intersection(x: float, y: float, axes: list, tolerance: float) -> tuple | None:
    """Find nearest axis intersection within tolerance. axes is list of GridAxis objects."""
    import math
    x_axes = [a for a in axes if a.direction == "X"]
    y_axes = [a for a in axes if a.direction == "Y"]
    intersections = build_axis_intersections(x_axes, y_axes)
    best = None
    best_d = tolerance
    for pt in intersections:
        d = math.hypot(pt[0] - x, pt[1] - y)
        if d <= best_d:
            best_d = d
            best = pt
    return best


def axes_from_spacing(direction: str, start: float, count: int, spacing: float,
                       prefix: str = "") -> list:
    """Generate evenly-spaced axes. E.g. direction='X', start=0, count=3, spacing=3640 → X1,X2,X3."""
    if not prefix:
        prefix = direction
    result = []
    for i in range(count):
        result.append(GridAxis(
            name="{}{}".format(prefix, i + 1),
            direction=direction,
            position=start + i * spacing,
        ))
    return result
