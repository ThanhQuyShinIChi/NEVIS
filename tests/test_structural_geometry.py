"""Tests for modules/structural_geometry.py — no Qt dependency."""
import pytest
from modules.structural_geometry import (
    rect_from_two_points, snap_to_grid, nearest_snap_point,
    rect_from_center_wl, rect_bounds, rect_contains, grid_points_in_view,
)


# --- rect_from_two_points ---

def test_rect_normal_order():
    r = rect_from_two_points((0, 0), (100, 200))
    assert r == [(0, 0), (100, 0), (100, 200), (0, 200)]

def test_rect_reversed_order():
    r = rect_from_two_points((100, 200), (0, 0))
    assert r == [(0, 0), (100, 0), (100, 200), (0, 200)]

def test_rect_partial_reverse():
    r = rect_from_two_points((50, 0), (0, 100))
    assert r[0] == (0, 0)
    assert r[2] == (50, 100)

def test_rect_has_four_corners():
    r = rect_from_two_points((10, 20), (30, 50))
    assert len(r) == 4


# --- snap_to_grid ---

def test_snap_303_exact():
    assert snap_to_grid(303.0, 606.0, 303.0) == (303.0, 606.0)

def test_snap_303_round_up():
    assert snap_to_grid(200.0, 0.0, 303.0) == (303.0, 0.0)

def test_snap_303_round_down():
    assert snap_to_grid(100.0, 0.0, 303.0) == (0.0, 0.0)

def test_snap_455():
    # 300 is closer to 455 than to 0
    x, y = snap_to_grid(300.0, 0.0, 455.0)
    assert x == 455.0

def test_snap_zero_grid_passthrough():
    assert snap_to_grid(123.4, 567.8, 0) == (123.4, 567.8)

def test_snap_negative_grid_passthrough():
    assert snap_to_grid(100.0, 200.0, -10.0) == (100.0, 200.0)


# --- nearest_snap_point ---

def test_nearest_within_tolerance():
    candidates = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]
    result = nearest_snap_point(95.0, 5.0, candidates, tolerance=20.0)
    assert result == (100.0, 0.0)

def test_nearest_outside_tolerance():
    candidates = [(0.0, 0.0), (100.0, 0.0)]
    result = nearest_snap_point(60.0, 0.0, candidates, tolerance=10.0)
    assert result is None

def test_nearest_empty_candidates():
    assert nearest_snap_point(0.0, 0.0, [], tolerance=100.0) is None

def test_nearest_exact_match():
    candidates = [(50.0, 50.0)]
    assert nearest_snap_point(50.0, 50.0, candidates, tolerance=0.0) == (50.0, 50.0)


# --- rect_from_center_wl ---

def test_center_wl_basic():
    r = rect_from_center_wl(500.0, 500.0, 200.0, 400.0)
    assert r[0] == (400.0, 300.0)
    assert r[2] == (600.0, 700.0)

def test_center_wl_symmetric():
    r = rect_from_center_wl(0.0, 0.0, 100.0, 100.0)
    xs = [p[0] for p in r]
    assert min(xs) == -50.0
    assert max(xs) == 50.0


# --- rect_bounds ---

def test_bounds_basic():
    pts = [(0, 0), (100, 0), (100, 200), (0, 200)]
    assert rect_bounds(pts) == (0, 0, 100, 200)

def test_bounds_unordered():
    pts = [(50, 50), (10, 90), (90, 10), (50, 50)]
    x0, y0, x1, y1 = rect_bounds(pts)
    assert x0 == 10 and x1 == 90


# --- rect_contains ---

def test_contains_true():
    outer = [(0, 0), (200, 0), (200, 200), (0, 200)]
    inner = [(50, 50), (150, 50), (150, 150), (50, 150)]
    assert rect_contains(outer, inner) is True

def test_contains_false_overlap():
    outer = [(0, 0), (100, 0), (100, 100), (0, 100)]
    inner = [(50, 50), (150, 50), (150, 150), (50, 150)]
    assert rect_contains(outer, inner) is False

def test_contains_exact_edge():
    outer = [(0, 0), (100, 0), (100, 100), (0, 100)]
    inner = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert rect_contains(outer, inner) is True


# --- grid_points_in_view ---

def test_grid_in_view_count():
    pts = grid_points_in_view(0, 0, 303, 303, 303)
    # corners: (0,0),(303,0),(0,303),(303,303)
    assert (0.0, 0.0) in pts
    assert (303.0, 303.0) in pts

def test_grid_max_points_respected():
    pts = grid_points_in_view(0, 0, 10000, 10000, 10, max_points=100)
    assert len(pts) <= 100

def test_grid_zero_spacing_empty():
    assert grid_points_in_view(0, 0, 1000, 1000, 0) == []
