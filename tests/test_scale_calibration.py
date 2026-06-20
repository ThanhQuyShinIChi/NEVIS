"""Tests for modules/scale_calibration.py — no Qt dependency."""
import pytest
from modules.scale_calibration import compute_scale, canvas_to_real, real_to_canvas, format_scale_ratio


# --- compute_scale ---

def test_scale_basic():
    # canvas: 200px apart, real: 10000mm → scale = 50
    scale = compute_scale((0.0, 0.0), (200.0, 0.0), 10000.0)
    assert scale == 50.0

def test_scale_diagonal():
    import math
    # 3-4-5 triangle: distance = 500
    scale = compute_scale((0.0, 0.0), (300.0, 400.0), 25000.0)
    assert abs(scale - 50.0) < 0.01

def test_scale_zero_distance_raises():
    with pytest.raises(ValueError):
        compute_scale((10.0, 10.0), (10.0, 10.0), 5000.0)

def test_scale_zero_real_raises():
    with pytest.raises(ValueError):
        compute_scale((0.0, 0.0), (100.0, 0.0), 0.0)

def test_scale_negative_real_raises():
    with pytest.raises(ValueError):
        compute_scale((0.0, 0.0), (100.0, 0.0), -500.0)


# --- canvas_to_real ---

def test_canvas_to_real_basic():
    x, y = canvas_to_real(100.0, 200.0, 50.0)
    assert x == 5000.0
    assert y == 10000.0

def test_canvas_to_real_with_origin():
    x, y = canvas_to_real(150.0, 200.0, 50.0, origin=(100.0, 0.0))
    assert x == 2500.0  # (150-100)*50

def test_canvas_to_real_zero():
    x, y = canvas_to_real(0.0, 0.0, 50.0)
    assert x == 0.0 and y == 0.0


# --- real_to_canvas ---

def test_real_to_canvas_basic():
    x, y = real_to_canvas(5000.0, 10000.0, 50.0)
    assert x == 100.0
    assert y == 200.0

def test_real_to_canvas_with_origin():
    x, y = real_to_canvas(0.0, 0.0, 50.0, origin=(10.0, 20.0))
    assert x == 10.0 and y == 20.0

def test_real_to_canvas_zero_scale_raises():
    with pytest.raises(ValueError):
        real_to_canvas(100.0, 200.0, 0.0)

def test_roundtrip():
    scale = 50.0
    origin = (50.0, 50.0)
    real_x, real_y = 3640.0, 2730.0
    cx, cy = real_to_canvas(real_x, real_y, scale, origin)
    back_x, back_y = canvas_to_real(cx, cy, scale, origin)
    assert abs(back_x - real_x) < 0.001
    assert abs(back_y - real_y) < 0.001


# --- format_scale_ratio ---

def test_format_1_50():
    assert format_scale_ratio(50.0) == "1:50"

def test_format_1_100():
    assert format_scale_ratio(100.0) == "1:100"

def test_format_zero_scale():
    assert format_scale_ratio(0) == "N/A"

def test_format_negative():
    assert format_scale_ratio(-1) == "N/A"
