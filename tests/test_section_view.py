"""Tests for modules/section_view.py — no Qt dependency."""
import pytest
from types import SimpleNamespace
from modules.section_view import (
    ElevationMarker, compute_fl, compute_ch,
    format_elevation_label, build_standard_markers,
    section_marker_to_dict, section_marker_from_dict,
    build_unified_slab_sections, merge_section_intervals, polygon_cut_intervals,
)


# --- compute_fl / compute_ch ---

def test_fl_default_finish():
    assert compute_fl(0.0) == 40.0

def test_fl_custom_finish():
    assert compute_fl(0.0, finish_thickness_mm=30.0) == 30.0

def test_fl_above_sl():
    assert compute_fl(100.0, 50.0) == 150.0

def test_ch_basic():
    # FL=40, ceiling_bottom=2440 → CH = 2440-40 = 2400
    assert compute_ch(40.0, 2440.0) == 2400.0

def test_ch_negative_if_ceiling_below_fl():
    assert compute_ch(40.0, 30.0) < 0


# --- format_elevation_label ---

def test_sl_zero():
    assert format_elevation_label("SL", 0.0) == "SL±0"

def test_sl_positive():
    assert format_elevation_label("SL", 100.0) == "SL+100"

def test_sl_negative():
    assert format_elevation_label("SL", -200.0) == "SL-200"

def test_sl_near_zero_rounds_to_zero():
    assert format_elevation_label("SL", 0.3) == "SL±0"


# --- build_standard_markers ---

def test_standard_markers_count_no_ceiling():
    markers = build_standard_markers(gl_mm=-500.0)
    # GL + SL + FL = 3
    assert len(markers) == 3

def test_standard_markers_count_with_ceiling():
    markers = build_standard_markers(gl_mm=-500.0, ceiling_bottom=2440.0)
    assert len(markers) == 4

def test_standard_markers_gl_first():
    markers = build_standard_markers(gl_mm=-600.0)
    assert markers[0].label == "GL"
    assert markers[0].elevation_mm == -600.0

def test_standard_markers_sl_zero():
    markers = build_standard_markers(gl_mm=-500.0, sl_mm=0.0)
    sl = next(m for m in markers if "SL" in m.label and "±" in m.label)
    assert sl.elevation_mm == 0.0

def test_standard_markers_fl_above_sl():
    markers = build_standard_markers(gl_mm=-500.0, sl_mm=0.0, finish_thickness=40.0)
    fl = next(m for m in markers if m.label == "FL")
    assert fl.elevation_mm == 40.0

def test_standard_markers_ch_label():
    markers = build_standard_markers(gl_mm=-500.0, ceiling_bottom=2440.0, ceiling_finish=12.5)
    ch = next(m for m in markers if "CH" in m.label)
    assert ch is not None


# --- round-trip ---

def test_marker_roundtrip():
    m = ElevationMarker(label="GL", elevation_mm=-600.0, color="#8B4513", line_style="solid")
    d = section_marker_to_dict(m)
    r = section_marker_from_dict(d)
    assert r.label == "GL"
    assert r.elevation_mm == -600.0
    assert r.color == "#8B4513"

def test_marker_from_dict_defaults():
    r = section_marker_from_dict({})
    assert r.label == ""
    assert r.elevation_mm == 0.0
    assert r.line_style == "solid"


# --- unified stepped-slab section geometry ---

def _slab(eid, points, top, bottom, stepped=False, parent_id=-1, overlap=0):
    return SimpleNamespace(
        id=eid,
        element_type="slab",
        points=points,
        top_elevation=top,
        bottom_elevation=bottom,
        height=top - bottom,
        is_stepped=stepped,
        parent_slab_id=parent_id,
        overlap_width=overlap,
    )


def test_polygon_cut_intervals_horizontal_rectangle():
    points = [(0, 0), (1000, 0), (1000, 500), (0, 500)]
    assert polygon_cut_intervals(points, "X", 250) == [(0.0, 1000.0)]


def test_polygon_cut_intervals_vertical_rectangle():
    points = [(0, 0), (1000, 0), (1000, 500), (0, 500)]
    assert polygon_cut_intervals(points, "Y", 400) == [(0.0, 500.0)]


def test_unified_section_replaces_parent_inside_stepped_core():
    parent = _slab(1, [(0, 0), (1000, 0), (1000, 500), (0, 500)], 0, -200)
    child = _slab(
        2, [(300, 100), (700, 100), (700, 400), (300, 400)],
        -75, -275, stepped=True, parent_id=1,
    )
    assembly = build_unified_slab_sections([parent, child], "X", 250)[0]
    parent_pieces = [p for p in assembly.pieces if not p.is_stepped]
    child_pieces = [p for p in assembly.pieces if p.is_stepped]
    assert [(p.start_mm, p.end_mm) for p in parent_pieces] == [(0.0, 300.0), (700.0, 1000.0)]
    assert [(p.start_mm, p.end_mm) for p in child_pieces] == [(300.0, 700.0)]


def test_unified_section_extends_child_by_overlap_width():
    parent = _slab(1, [(0, 0), (1000, 0), (1000, 500), (0, 500)], 0, -200)
    child = _slab(
        2, [(300, 100), (700, 100), (700, 400), (300, 400)],
        -75, -275, stepped=True, parent_id=1, overlap=60,
    )
    assembly = build_unified_slab_sections([parent, child], "X", 250)[0]
    child_piece = next(p for p in assembly.pieces if p.is_stepped)
    assert (child_piece.start_mm, child_piece.end_mm) == (240.0, 760.0)
    assert child_piece.marker_mm == 300.0
    assert [(b.start_mm, b.end_mm) for b in assembly.overlap_bands] == [
        (240.0, 300.0), (700.0, 760.0),
    ]


def test_finish_union_removes_parent_child_overlap():
    parent = _slab(1, [(0, 0), (1000, 0), (1000, 500), (0, 500)], 0, -200)
    child = _slab(
        2, [(300, 100), (700, 100), (700, 400), (300, 400)],
        -75, -275, stepped=True, parent_id=1, overlap=60,
    )
    assembly = build_unified_slab_sections([parent, child], "X", 250)[0]

    finish_intervals = merge_section_intervals(
        [(piece.start_mm, piece.end_mm) for piece in assembly.pieces]
    )

    assert finish_intervals == [(0.0, 1000.0)]


def test_unified_section_matches_logged_vertical_cut_geometry():
    parent = _slab(
        1,
        [(-1720, -850), (-550, -850), (-550, -270), (-1720, -270)],
        0, -200,
    )
    child = _slab(
        2,
        [(-1539.1255, -795), (-1010, -795), (-1010, -346.7595), (-1539.1255, -346.7595)],
        -75, -275, stepped=True, parent_id=1, overlap=60,
    )
    assembly = build_unified_slab_sections([parent, child], "Y", -1354.24)[0]
    parent_ranges = [(p.start_mm, p.end_mm) for p in assembly.pieces if not p.is_stepped]
    stepped_range = next((p.start_mm, p.end_mm) for p in assembly.pieces if p.is_stepped)
    assert parent_ranges == [(-850.0, -795.0), (-346.7595, -270.0)]
    assert stepped_range == (-850.0, -286.7595)
