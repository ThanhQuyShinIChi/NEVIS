"""Tests for modules/structural_element.py — no Qt dependency."""
import pytest
from modules.structural_element import (
    StructuralElement,
    structural_element_to_dict,
    structural_element_from_dict,
    VALID_TYPES,
)


def _roundtrip(e: StructuralElement) -> StructuralElement:
    return structural_element_from_dict(structural_element_to_dict(e))


# --- round-trip for each element_type ---

def test_roundtrip_slab():
    e = StructuralElement(id=1, element_type="slab", height=150.0, top_elevation=-50.0, bottom_elevation=-200.0)
    r = _roundtrip(e)
    assert r.id == 1
    assert r.element_type == "slab"
    assert r.height == 150.0
    assert r.top_elevation == -50.0
    assert r.bottom_elevation == -200.0

def test_roundtrip_beam():
    e = StructuralElement(id=2, element_type="beam", width=300.0, height=600.0, label="GL梁")
    r = _roundtrip(e)
    assert r.element_type == "beam"
    assert r.width == 300.0
    assert r.height == 600.0
    assert r.label == "GL梁"

def test_roundtrip_column():
    e = StructuralElement(id=3, element_type="column", width=500.0, length=500.0)
    r = _roundtrip(e)
    assert r.element_type == "column"
    assert r.width == 500.0

def test_roundtrip_wall_rc():
    e = StructuralElement(id=4, element_type="wall_rc", height=2800.0, width=200.0)
    r = _roundtrip(e)
    assert r.element_type == "wall_rc"
    assert r.height == 2800.0

def test_roundtrip_wall_lgs():
    e = StructuralElement(
        id=5, element_type="wall_lgs",
        stud_spacing=455.0, stud_width=100.0,
        board_thickness=15.0, board_layers=2,
    )
    r = _roundtrip(e)
    assert r.element_type == "wall_lgs"
    assert r.stud_spacing == 455.0
    assert r.stud_width == 100.0
    assert r.board_thickness == 15.0
    assert r.board_layers == 2

def test_roundtrip_ceiling():
    e = StructuralElement(id=6, element_type="ceiling", top_elevation=-2400.0)
    r = _roundtrip(e)
    assert r.element_type == "ceiling"
    assert r.top_elevation == -2400.0

def test_roundtrip_with_arc():
    e = StructuralElement(id=7, element_type="slab", arc_radius=1500.0)
    r = _roundtrip(e)
    assert r.arc_radius == 1500.0

def test_roundtrip_stepped_slab():
    e = StructuralElement(
        id=8, element_type="slab",
        is_stepped=True, parent_slab_id=1, overlap_width=200.0,
        top_elevation=-200.0,
    )
    r = _roundtrip(e)
    assert r.is_stepped is True
    assert r.parent_slab_id == 1
    assert r.overlap_width == 200.0

def test_roundtrip_points():
    pts = [(0.0, 0.0), (1000.0, 0.0), (1000.0, 2000.0), (0.0, 2000.0)]
    e = StructuralElement(id=9, element_type="slab", points=pts)
    r = _roundtrip(e)
    assert len(r.points) == 4
    assert r.points[0] == (0.0, 0.0)
    assert r.points[2] == (1000.0, 2000.0)


# --- missing fields → safe defaults ---

def test_missing_all_fields_defaults():
    r = structural_element_from_dict({"id": 10, "element_type": "slab"})
    assert r.width == 0.0
    assert r.height == 0.0
    assert r.stud_spacing == 303.0
    assert r.board_layers == 1
    assert r.is_stepped is False
    assert r.parent_slab_id == -1

def test_missing_id_defaults_zero():
    r = structural_element_from_dict({"element_type": "beam"})
    assert r.id == 0

def test_invalid_element_type_falls_back_to_slab():
    r = structural_element_from_dict({"id": 1, "element_type": "unknown_type"})
    assert r.element_type == "slab"

def test_missing_points_defaults_empty():
    r = structural_element_from_dict({"id": 1, "element_type": "column"})
    assert r.points == []

def test_bad_numeric_field_defaults():
    r = structural_element_from_dict({"id": 1, "element_type": "slab", "height": "bad", "width": None})
    assert r.height == 0.0
    assert r.width == 0.0

def test_empty_dict_no_crash():
    r = structural_element_from_dict({})
    assert r.element_type == "slab"
    assert r.id == 0


# --- VALID_TYPES ---

def test_valid_types_contains_all():
    assert "slab" in VALID_TYPES
    assert "wall_lgs" in VALID_TYPES
    assert "ceiling" in VALID_TYPES
