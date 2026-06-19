"""Tests for modules/grid_axis.py — no Qt dependency."""
import pytest
from modules.grid_axis import (
    GridAxis, grid_axis_to_dict, grid_axis_from_dict,
    build_axis_intersections, find_nearest_axis_intersection, axes_from_spacing,
)


# --- round-trip ---

def test_roundtrip_x_axis():
    a = GridAxis(name="X1", direction="X", position=0.0)
    d = grid_axis_to_dict(a)
    r = grid_axis_from_dict(d)
    assert r.name == "X1"
    assert r.direction == "X"
    assert r.position == 0.0

def test_roundtrip_y_axis():
    a = GridAxis(name="Y2", direction="Y", position=3640.0)
    r = grid_axis_from_dict(grid_axis_to_dict(a))
    assert r.direction == "Y"
    assert r.position == 3640.0

def test_from_dict_invalid_direction():
    r = grid_axis_from_dict({"name": "Z1", "direction": "Z", "position": 100.0})
    assert r.direction == "X"

def test_from_dict_bad_position():
    r = grid_axis_from_dict({"name": "X1", "direction": "X", "position": "bad"})
    assert r.position == 0.0

def test_from_dict_empty():
    r = grid_axis_from_dict({})
    assert r.name == ""
    assert r.direction == "X"


# --- build_axis_intersections ---

def test_intersections_2x2():
    x_axes = [GridAxis("X1", "X", 0.0), GridAxis("X2", "X", 3640.0)]
    y_axes = [GridAxis("Y1", "Y", 0.0), GridAxis("Y2", "Y", 2730.0)]
    pts = build_axis_intersections(x_axes, y_axes)
    assert len(pts) == 4
    assert (0.0, 0.0) in pts
    assert (3640.0, 2730.0) in pts

def test_intersections_empty_x():
    pts = build_axis_intersections([], [GridAxis("Y1", "Y", 0.0)])
    assert pts == []

def test_intersections_single():
    pts = build_axis_intersections(
        [GridAxis("X1", "X", 100.0)],
        [GridAxis("Y1", "Y", 200.0)],
    )
    assert pts == [(100.0, 200.0)]


# --- find_nearest_axis_intersection ---

def _axes_2x2():
    return [
        GridAxis("X1", "X", 0.0), GridAxis("X2", "X", 3640.0),
        GridAxis("Y1", "Y", 0.0), GridAxis("Y2", "Y", 2730.0),
    ]

def test_nearest_within_tolerance():
    axes = _axes_2x2()
    result = find_nearest_axis_intersection(5.0, 5.0, axes, tolerance=20.0)
    assert result == (0.0, 0.0)

def test_nearest_outside_tolerance():
    axes = _axes_2x2()
    result = find_nearest_axis_intersection(200.0, 200.0, axes, tolerance=10.0)
    assert result is None

def test_nearest_far_corner():
    axes = _axes_2x2()
    result = find_nearest_axis_intersection(3638.0, 2732.0, axes, tolerance=10.0)
    assert result == (3640.0, 2730.0)


# --- axes_from_spacing ---

def test_spacing_x_3_axes():
    axes = axes_from_spacing("X", start=0.0, count=3, spacing=3640.0)
    assert len(axes) == 3
    assert axes[0].name == "X1"
    assert axes[1].position == 3640.0
    assert axes[2].position == 7280.0

def test_spacing_custom_prefix():
    axes = axes_from_spacing("Y", start=0.0, count=2, spacing=2730.0, prefix="GL")
    assert axes[0].name == "GL1"
    assert axes[0].direction == "Y"

def test_spacing_zero_count():
    axes = axes_from_spacing("X", 0.0, 0, 3640.0)
    assert axes == []
