"""Tests for modules/grid_axis.py — Task 14."""
import pytest
from modules.grid_axis import (
    GridAxis,
    grid_axis_to_dict,
    grid_axis_from_dict,
    build_axis_intersections,
    find_nearest_axis_intersection,
)


class TestGridAxisSerialize:
    def test_round_trip_x(self):
        axis = GridAxis(name="X1", direction="X", position=0.0)
        assert grid_axis_from_dict(grid_axis_to_dict(axis)) == axis

    def test_round_trip_y(self):
        axis = GridAxis(name="Y2", direction="Y", position=3640.0)
        assert grid_axis_from_dict(grid_axis_to_dict(axis)) == axis

    def test_from_dict_defaults(self):
        axis = grid_axis_from_dict({})
        assert axis.name == ""
        assert axis.direction == "X"
        assert axis.position == 0.0

    def test_to_dict_keys(self):
        d = grid_axis_to_dict(GridAxis("X3", "X", 7280.0))
        assert set(d.keys()) == {"name", "direction", "position"}
        assert d["position"] == 7280.0


class TestBuildIntersections:
    def _make_grid(self):
        x_axes = [
            GridAxis("X1", "X", 0.0),
            GridAxis("X2", "X", 3640.0),
            GridAxis("X3", "X", 7280.0),
        ]
        y_axes = [
            GridAxis("Y1", "Y", 0.0),
            GridAxis("Y2", "Y", 3640.0),
        ]
        return x_axes, y_axes

    def test_count(self):
        x_axes, y_axes = self._make_grid()
        pts = build_axis_intersections(x_axes, y_axes)
        assert len(pts) == 6  # 3 X × 2 Y

    def test_values(self):
        x_axes, y_axes = self._make_grid()
        pts = build_axis_intersections(x_axes, y_axes)
        assert (0.0, 0.0) in pts
        assert (3640.0, 3640.0) in pts
        assert (7280.0, 0.0) in pts

    def test_empty_x(self):
        assert build_axis_intersections([], [GridAxis("Y1", "Y", 0.0)]) == []

    def test_empty_y(self):
        assert build_axis_intersections([GridAxis("X1", "X", 0.0)], []) == []

    def test_wrong_direction_ignored(self):
        # If we pass X axes as Y group, no intersections
        x_axes = [GridAxis("X1", "X", 0.0)]
        result = build_axis_intersections(x_axes, x_axes)
        assert result == []


class TestFindNearestAxisIntersection:
    def _axes(self):
        return [
            GridAxis("X1", "X", 0.0),
            GridAxis("X2", "X", 3640.0),
            GridAxis("Y1", "Y", 0.0),
            GridAxis("Y2", "Y", 3640.0),
        ]

    def test_exact_hit(self):
        pt = find_nearest_axis_intersection(0.0, 0.0, self._axes(), tolerance=15.0)
        assert pt == (0.0, 0.0)

    def test_near_hit(self):
        pt = find_nearest_axis_intersection(10.0, 5.0, self._axes(), tolerance=20.0)
        assert pt == (0.0, 0.0)

    def test_outside_tolerance(self):
        pt = find_nearest_axis_intersection(100.0, 100.0, self._axes(), tolerance=15.0)
        assert pt is None

    def test_picks_nearest(self):
        pt = find_nearest_axis_intersection(3645.0, 3638.0, self._axes(), tolerance=20.0)
        assert pt == (3640.0, 3640.0)

    def test_empty_axes(self):
        assert find_nearest_axis_intersection(0.0, 0.0, [], 100.0) is None
