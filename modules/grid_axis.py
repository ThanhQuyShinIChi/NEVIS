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


def next_axis_name(axes: list, direction: str) -> str:
    """Auto-generate next name like X1, X2, Y1, Y2 for the given direction."""
    prefix = direction.upper()
    existing = [a for a in axes if a.direction == direction]
    return "{}{}".format(prefix, len(existing) + 1)


def rename_axes_prefix(axes: list, direction: str, new_prefix: str) -> list:
    """Return new list with all axes of given direction renamed to new_prefix+index.

    Axes of other direction are unchanged. Index restarts from 1.
    """
    new_prefix = new_prefix.upper().strip() or direction.upper()
    result = []
    counter = 1
    for a in axes:
        if a.direction == direction:
            result.append(GridAxis(
                name="{}{}".format(new_prefix, counter),
                direction=a.direction,
                position=a.position,
            ))
            counter += 1
        else:
            result.append(a)
    return result


def sort_axes_xy(axes: list) -> list:
    """Return axes sorted: X-direction first (by position), then Y-direction (by position)."""
    x = sorted([a for a in axes if a.direction == "X"], key=lambda a: a.position)
    y = sorted([a for a in axes if a.direction == "Y"], key=lambda a: a.position)
    return x + y


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
