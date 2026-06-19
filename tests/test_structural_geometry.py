from __future__ import annotations

from modules.structural_geometry import (
    nearest_snap_point,
    rect_from_two_points,
    snap_to_grid,
)


def test_rect_from_two_points_normalizes_all_drag_directions() -> None:
    expected = [(10.0, 20.0), (50.0, 20.0), (50.0, 80.0), (10.0, 80.0)]

    assert rect_from_two_points((10, 20), (50, 80)) == expected
    assert rect_from_two_points((50, 80), (10, 20)) == expected
    assert rect_from_two_points((50, 20), (10, 80)) == expected


def test_snap_to_grid_rounds_each_coordinate() -> None:
    assert snap_to_grid(149.0, 151.0, 100.0) == (100.0, 200.0)
    assert snap_to_grid(-149.0, -151.0, 100.0) == (-100.0, -200.0)
    assert snap_to_grid(150.0, -150.0, 100.0) == (200.0, -200.0)


def test_snap_to_grid_with_invalid_grid_returns_original_point() -> None:
    assert snap_to_grid(12.5, 37.5, 0.0) == (12.5, 37.5)
    assert snap_to_grid(12.5, 37.5, -10.0) == (12.5, 37.5)


def test_nearest_snap_point_returns_nearest_candidate_in_tolerance() -> None:
    candidates = [(0.0, 0.0), (8.0, 6.0), (30.0, 30.0)]

    assert nearest_snap_point(10.0, 8.0, candidates, 5.0) == (8.0, 6.0)


def test_nearest_snap_point_includes_boundary_and_returns_none_outside() -> None:
    assert nearest_snap_point(0.0, 0.0, [(3.0, 4.0)], 5.0) == (3.0, 4.0)
    assert nearest_snap_point(0.0, 0.0, [(3.0, 4.0)], 4.99) is None
    assert nearest_snap_point(0.0, 0.0, [], 10.0) is None


def test_nearest_snap_point_keeps_first_candidate_when_distances_tie() -> None:
    assert nearest_snap_point(0.0, 0.0, [(3.0, 4.0), (-3.0, -4.0)], 5.0) == (3.0, 4.0)
