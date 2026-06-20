"""Tests for modules/clash_detection.py — no Qt dependency."""
import pytest
from modules.clash_detection import (
    ClashResult,
    check_elevation_clash,
    find_clashes,
    point_in_polygon,
    segment_intersects_polygon,
)


# ---------------------------------------------------------------------------
# point_in_polygon
# ---------------------------------------------------------------------------

def test_point_inside_square():
    poly = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert point_in_polygon(50, 50, poly) is True


def test_point_outside_square():
    poly = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert point_in_polygon(200, 200, poly) is False


def test_point_clearly_outside():
    poly = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert point_in_polygon(-1, 50, poly) is False


def test_point_inside_triangle():
    poly = [(0, 0), (100, 0), (50, 100)]
    assert point_in_polygon(50, 30, poly) is True


def test_point_outside_triangle():
    poly = [(0, 0), (100, 0), (50, 100)]
    assert point_in_polygon(90, 90, poly) is False


# ---------------------------------------------------------------------------
# check_elevation_clash
# ---------------------------------------------------------------------------

def test_pipe_inside_slab():
    # Sàn top=0, bottom=-150 — ống z=-80 → clash penetrate
    is_clash, overlap = check_elevation_clash(-80, -150, 0)
    assert is_clash is True
    assert overlap >= 0


def test_pipe_below_slab_ok():
    # Ống z=-300 — dưới đáy sàn SL-150 → không clash
    is_clash, _ = check_elevation_clash(-300, -150, 0)
    assert is_clash is False


def test_pipe_above_slab_ok():
    is_clash, _ = check_elevation_clash(100, -150, 0)
    assert is_clash is False


def test_pipe_exactly_on_top():
    # z == top_elevation → nằm trong phần tử → clash
    is_clash, overlap = check_elevation_clash(0, -150, 0)
    assert is_clash is True
    assert overlap >= 0


def test_pipe_exactly_on_bottom():
    is_clash, overlap = check_elevation_clash(-150, -150, 0)
    assert is_clash is True
    assert overlap >= 0


def test_pipe_too_close_below():
    # Ống z=-170, clearance=50 → cách đáy sàn 20mm < 50 → too_close
    is_clash, overlap = check_elevation_clash(-170, -150, 0, clearance_mm=50)
    assert is_clash is True
    assert overlap < 0


def test_pipe_far_enough_below():
    # Ống z=-210, clearance=50 → cách đáy sàn 60mm > 50 → OK
    is_clash, _ = check_elevation_clash(-210, -150, 0, clearance_mm=50)
    assert is_clash is False


def test_pipe_too_close_above():
    # Ống z=30, clearance=50 → cách đỉnh sàn 30mm < 50 → too_close
    is_clash, overlap = check_elevation_clash(30, -150, 0, clearance_mm=50)
    assert is_clash is True
    assert overlap < 0


def test_overlap_mm_is_symmetric():
    # z ở giữa phần tử → overlap = khoảng cách đến cạnh gần hơn
    _, overlap = check_elevation_clash(-75, -150, 0)
    assert overlap == pytest.approx(75.0)


# ---------------------------------------------------------------------------
# segment_intersects_polygon
# ---------------------------------------------------------------------------

def test_segment_crosses_square():
    poly = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
    assert segment_intersects_polygon((-100, 500), (1100, 500), poly) is True


def test_segment_outside_square():
    poly = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert segment_intersects_polygon((200, 0), (200, 100), poly) is False


def test_segment_entirely_inside():
    poly = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
    assert segment_intersects_polygon((100, 100), (900, 900), poly) is True


def test_segment_touches_one_endpoint_inside():
    poly = [(0, 0), (1000, 0), (1000, 1000), (0, 1000)]
    assert segment_intersects_polygon((500, 500), (2000, 500), poly) is True


# ---------------------------------------------------------------------------
# find_clashes — mock objects
# ---------------------------------------------------------------------------

class _Pipe:
    def __init__(self, id, z, points):
        self.id = id
        self.z_elevation = z
        self.points = points


class _Elem:
    def __init__(self, id, etype, points, top, bottom):
        self.id = id
        self.element_type = etype
        self.points = points
        self.top_elevation = top
        self.bottom_elevation = bottom


_SLAB = _Elem(1, "slab", [(0, 0), (1000, 0), (1000, 1000), (0, 1000)], 0, -150)


def test_find_clashes_one_penetrate():
    pipe = _Pipe(1, -80, [(500, -100), (500, 1100)])
    results = find_clashes([pipe], [_SLAB])
    assert len(results) == 1
    assert results[0].clash_type == "penetrate"
    assert results[0].element_type == "slab"
    assert results[0].pipe_id == 1
    assert results[0].element_id == 1


def test_find_clashes_no_clash_z_ok():
    pipe = _Pipe(1, -300, [(500, -100), (500, 1100)])
    assert find_clashes([pipe], [_SLAB]) == []


def test_find_clashes_no_clash_xy_miss():
    pipe = _Pipe(1, -80, [(2000, 0), (2000, 1000)])
    assert find_clashes([pipe], [_SLAB]) == []


def test_find_clashes_too_close():
    pipe = _Pipe(1, -170, [(500, -100), (500, 1100)])
    results = find_clashes([pipe], [_SLAB], clearance_mm=50)
    assert len(results) == 1
    assert results[0].clash_type == "too_close"
    assert results[0].overlap_mm < 0


def test_find_clashes_multiple_pipes():
    p1 = _Pipe(1, -80, [(500, -100), (500, 1100)])    # clash
    p2 = _Pipe(2, -300, [(500, -100), (500, 1100)])   # z ok
    p3 = _Pipe(3, -80, [(2000, 0), (2000, 1000)])     # xy miss
    results = find_clashes([p1, p2, p3], [_SLAB])
    assert len(results) == 1
    assert results[0].pipe_id == 1


def test_find_clashes_multiple_elements():
    beam = _Elem(2, "beam", [(0, 0), (1000, 0), (1000, 1000), (0, 1000)], 0, -600)
    pipe = _Pipe(1, -400, [(500, -100), (500, 1100)])  # z trong dầm
    results = find_clashes([pipe], [_SLAB, beam])
    # z=-400 nằm trong beam (top=0, bottom=-600) → clash với beam
    # z=-400 không trong slab (top=0, bottom=-150) → không clash với slab
    element_types = {r.element_type for r in results}
    assert "beam" in element_types
    assert "slab" not in element_types


def test_find_clashes_pipe_no_points():
    pipe = _Pipe(1, -80, [])
    assert find_clashes([pipe], [_SLAB]) == []


def test_find_clashes_pipe_single_point():
    pipe = _Pipe(1, -80, [(500, 500)])
    assert find_clashes([pipe], [_SLAB]) == []


def test_find_clashes_elem_too_few_points():
    bad_elem = _Elem(1, "slab", [(0, 0), (100, 0)], 0, -150)  # chỉ 2 điểm
    pipe = _Pipe(1, -80, [(50, -100), (50, 100)])
    assert find_clashes([pipe], [bad_elem]) == []


def test_find_clashes_empty_inputs():
    assert find_clashes([], [_SLAB]) == []
    pipe = _Pipe(1, -80, [(500, -100), (500, 1100)])
    assert find_clashes([pipe], []) == []


def test_find_clashes_beam_same_xy():
    # Dầm và sàn cùng XY, ống đi qua — z quyết định clash với phần tử nào
    slab = _Elem(1, "slab", [(0, 0), (1000, 0), (1000, 1000), (0, 1000)], 0, -150)
    beam = _Elem(2, "beam", [(0, 0), (1000, 0), (1000, 1000), (0, 1000)], -150, -750)
    pipe_in_slab = _Pipe(1, -80, [(500, -100), (500, 1100)])
    pipe_in_beam = _Pipe(2, -400, [(500, -100), (500, 1100)])
    r1 = find_clashes([pipe_in_slab], [slab, beam])
    r2 = find_clashes([pipe_in_beam], [slab, beam])
    assert any(r.element_type == "slab" for r in r1)
    assert not any(r.element_type == "beam" for r in r1)
    assert any(r.element_type == "beam" for r in r2)
    assert not any(r.element_type == "slab" for r in r2)
