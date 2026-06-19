"""Tests for modules/section_view.py — no Qt dependency."""
import pytest
from modules.section_view import (
    ElevationMarker, compute_fl, compute_ch,
    format_elevation_label, build_standard_markers,
    section_marker_to_dict, section_marker_from_dict,
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
