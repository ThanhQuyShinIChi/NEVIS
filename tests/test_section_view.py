"""Tests for modules/section_view.py — Task 15."""
import pytest
from dataclasses import dataclass, field
from modules.section_view import (
    compute_fl,
    compute_ch,
    elements_intersect_cut_line,
    sort_elements_by_elevation,
)


@dataclass
class _MockElement:
    points: list = field(default_factory=list)
    bottom_elevation: float = 0.0
    element_type: str = "slab"


class TestComputeFL:
    def test_basic(self):
        assert compute_fl(0.0, 30.0) == 30.0

    def test_negative_sl(self):
        assert compute_fl(-200.0, 30.0) == -170.0

    def test_zero_finish(self):
        assert compute_fl(100.0, 0.0) == 100.0


class TestComputeCH:
    def test_basic(self):
        # ceiling at 2700, FL at 30 → CH = 2670
        assert compute_ch(2700.0, 30.0) == 2670.0

    def test_negative(self):
        assert compute_ch(2000.0, 2500.0) == -500.0


class TestElementsIntersectCutLine:
    def _slab(self, x0, y0, x1, y1):
        return _MockElement(points=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

    def test_intersects_horizontal(self):
        slab = self._slab(0, 0, 3000, 3000)
        # Horizontal cut through middle
        result = elements_intersect_cut_line([slab], (-500, 1500), (4000, 1500))
        assert slab in result

    def test_misses(self):
        slab = self._slab(0, 0, 3000, 3000)
        # Line above the slab
        result = elements_intersect_cut_line([slab], (0, -100), (3000, -100))
        assert slab not in result

    def test_diagonal_cut(self):
        slab = self._slab(1000, 1000, 4000, 4000)
        result = elements_intersect_cut_line([slab], (0, 0), (5000, 5000))
        assert slab in result

    def test_empty_elements(self):
        assert elements_intersect_cut_line([], (0, 0), (1000, 0)) == []

    def test_skips_degenerate(self):
        bad = _MockElement(points=[(0, 0)])  # only 1 point
        result = elements_intersect_cut_line([bad], (0, 0), (1000, 0))
        assert bad not in result

    def test_multiple_only_intersected(self):
        slab_a = self._slab(0, 0, 2000, 2000)
        slab_b = self._slab(5000, 5000, 8000, 8000)
        result = elements_intersect_cut_line([slab_a, slab_b], (-500, 1000), (3000, 1000))
        assert slab_a in result
        assert slab_b not in result


class TestSortElementsByElevation:
    def test_sorted_ascending(self):
        e1 = _MockElement(bottom_elevation=200.0)
        e2 = _MockElement(bottom_elevation=-300.0)
        e3 = _MockElement(bottom_elevation=0.0)
        result = sort_elements_by_elevation([e1, e2, e3])
        assert result == [e2, e3, e1]

    def test_empty(self):
        assert sort_elements_by_elevation([]) == []

    def test_single(self):
        e = _MockElement(bottom_elevation=500.0)
        assert sort_elements_by_elevation([e]) == [e]
