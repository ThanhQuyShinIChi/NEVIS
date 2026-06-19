"""Tests for modules/stepped_slab.py — no Qt dependency."""
import pytest
from modules.structural_element import StructuralElement
from modules.stepped_slab import (
    validate_stepped_slab_bounds,
    compute_stepped_slab_elevation,
    stepped_slab_overlap_region,
)


def _slab(pts):
    return StructuralElement(id=1, element_type="slab", points=pts)


PARENT_PTS = [(0.0, 0.0), (1000.0, 0.0), (1000.0, 800.0), (0.0, 800.0)]
CHILD_IN = [(100.0, 100.0), (400.0, 100.0), (400.0, 400.0), (100.0, 400.0)]
CHILD_OUT = [(900.0, 700.0), (1100.0, 700.0), (1100.0, 900.0), (900.0, 900.0)]


# --- validate_stepped_slab_bounds ---

def test_child_inside_parent():
    parent = _slab(PARENT_PTS)
    child = _slab(CHILD_IN)
    assert validate_stepped_slab_bounds(parent, child) is True

def test_child_outside_parent():
    parent = _slab(PARENT_PTS)
    child = _slab(CHILD_OUT)
    assert validate_stepped_slab_bounds(parent, child) is False

def test_empty_parent_returns_false():
    parent = _slab([])
    child = _slab(CHILD_IN)
    assert validate_stepped_slab_bounds(parent, child) is False

def test_empty_child_returns_false():
    parent = _slab(PARENT_PTS)
    child = _slab([])
    assert validate_stepped_slab_bounds(parent, child) is False

def test_exact_same_bounds():
    parent = _slab(PARENT_PTS)
    child = _slab(PARENT_PTS)
    assert validate_stepped_slab_bounds(parent, child) is True


# --- compute_stepped_slab_elevation ---

def test_elevation_200mm_below_sl():
    assert compute_stepped_slab_elevation(0.0, 200.0) == -200.0

def test_elevation_from_nonzero_sl():
    # sl_elevation = 100, offset = 50 → top = 50
    assert compute_stepped_slab_elevation(100.0, 50.0) == 50.0

def test_elevation_negative_offset_treated_as_abs():
    # offset given as -200 should still go downward
    assert compute_stepped_slab_elevation(0.0, -200.0) == -200.0

def test_elevation_zero_offset():
    assert compute_stepped_slab_elevation(0.0, 0.0) == 0.0


# --- stepped_slab_overlap_region ---

def test_overlap_region_basic():
    parent = _slab(PARENT_PTS)
    child = _slab(CHILD_IN)  # (100,100)-(400,400)
    region = stepped_slab_overlap_region(parent, child, overlap_width=50.0)
    assert len(region) == 4
    xs = [p[0] for p in region]
    assert min(xs) == 150.0  # 100 + 50
    assert max(xs) == 350.0  # 400 - 50

def test_overlap_region_too_large():
    parent = _slab(PARENT_PTS)
    child = _slab(CHILD_IN)
    # overlap_width larger than half child size → empty
    region = stepped_slab_overlap_region(parent, child, overlap_width=200.0)
    assert region == []

def test_overlap_region_empty_child():
    parent = _slab(PARENT_PTS)
    child = _slab([])
    assert stepped_slab_overlap_region(parent, child, overlap_width=50.0) == []


# --- serialize round-trip for stepped slab ---

def test_stepped_slab_roundtrip():
    from modules.structural_element import structural_element_to_dict, structural_element_from_dict
    e = StructuralElement(
        id=10, element_type="slab",
        is_stepped=True, parent_slab_id=1, overlap_width=150.0,
        top_elevation=-200.0, points=CHILD_IN,
    )
    d = structural_element_to_dict(e)
    r = structural_element_from_dict(d)
    assert r.is_stepped is True
    assert r.parent_slab_id == 1
    assert r.overlap_width == 150.0
    assert r.top_elevation == -200.0
