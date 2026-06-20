"""Tests for modules/structural_transform.py — no Qt dependency."""
import pytest
from modules.structural_element import StructuralElement
from modules.structural_transform import move_element, resize_element, element_handle_positions


def _elem(pts=None):
    pts = pts or [(0.0, 0.0), (200.0, 0.0), (200.0, 100.0), (0.0, 100.0)]
    return StructuralElement(id=1, element_type="slab", points=pts, width=200.0, length=100.0)


# --- move_element ---

def test_move_translates_all_points():
    e = _elem()
    r = move_element(e, 50, 30)
    assert r.points[0] == (50.0, 30.0)
    assert r.points[2] == (250.0, 130.0)

def test_move_zero():
    e = _elem()
    r = move_element(e, 0, 0)
    assert r.points == e.points

def test_move_negative():
    e = _elem()
    r = move_element(e, -100, -50)
    assert r.points[0] == (-100.0, -50.0)

def test_move_preserves_type():
    e = _elem()
    r = move_element(e, 10, 10)
    assert r.element_type == "slab"


# --- resize_element ---

def test_resize_br_handle():
    e = _elem()  # (0,0)-(200,100)
    r = resize_element(e, "br", (300.0, 150.0))
    bounds_x = [p[0] for p in r.points]
    bounds_y = [p[1] for p in r.points]
    assert max(bounds_x) == 300.0
    assert max(bounds_y) == 150.0

def test_resize_tl_handle():
    e = _elem()
    r = resize_element(e, "tl", (-50.0, -50.0))
    assert min(p[0] for p in r.points) == -50.0

def test_resize_top_handle():
    e = _elem()
    r = resize_element(e, "t", (0, -20.0))
    assert min(p[1] for p in r.points) == -20.0

def test_resize_empty_element():
    e = StructuralElement(id=1, element_type="slab")
    r = resize_element(e, "br", (100, 100))
    assert r.points == []

def test_resize_width_updated():
    e = _elem()  # w=200
    r = resize_element(e, "r", (300.0, 0.0))
    assert r.width == 300.0


# --- element_handle_positions ---

def test_handle_positions_count():
    e = _elem()
    h = element_handle_positions(e)
    assert len(h) == 8

def test_handle_tl_is_top_left():
    e = _elem()
    h = element_handle_positions(e)
    assert h["tl"] == (0.0, 0.0)

def test_handle_br_is_bottom_right():
    e = _elem()
    h = element_handle_positions(e)
    assert h["br"] == (200.0, 100.0)

def test_handle_empty_element():
    e = StructuralElement(id=1, element_type="slab")
    assert element_handle_positions(e) == {}
