from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class GridAxis:
    name: str        # "X1", "X2", "Y1", "Y2" ...
    direction: str   # "X" (vertical line) or "Y" (horizontal line)
    position: float  # real-world coordinate (mm)


def grid_axis_to_dict(axis: GridAxis) -> dict:
    return {"name": axis.name, "direction": axis.direction, "position": float(axis.position)}


def grid_axis_from_dict(d: dict) -> GridAxis:
    return GridAxis(
        name=str(d.get("name", "")),
        direction=str(d.get("direction", "X")),
        position=float(d.get("position", 0.0)),
    )


def build_axis_intersections(
    x_axes: list[GridAxis], y_axes: list[GridAxis]
) -> list[tuple[float, float]]:
    """Return all (x, y) intersections between X-direction and Y-direction axes."""
    return [
        (xa.position, ya.position)
        for xa in x_axes if xa.direction == "X"
        for ya in y_axes if ya.direction == "Y"
    ]


def find_nearest_axis_intersection(
    x: float,
    y: float,
    axes: list[GridAxis],
    tolerance: float,
) -> tuple[float, float] | None:
    """Find the nearest intersection of X and Y axes within tolerance.

    Also snaps to a single axis line (midpoint) when only one direction matches.
    """
    x_axes = [a for a in axes if a.direction == "X"]
    y_axes = [a for a in axes if a.direction == "Y"]
    intersections = build_axis_intersections(x_axes, y_axes)
    best: tuple[float, float] | None = None
    best_dist = tolerance
    for ix, iy in intersections:
        d = math.hypot(x - ix, y - iy)
        if d < best_dist:
            best_dist = d
            best = (ix, iy)
    return best
