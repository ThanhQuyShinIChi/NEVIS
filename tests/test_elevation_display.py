"""Tests for modules/elevation_display.py — no Qt dependency."""
import pytest
from modules.elevation_display import (
    compute_edge_slope,
    edge_elevation_labels,
    format_slope_label,
    format_z_label,
)


def test_compute_edge_slope_falling():
    assert compute_edge_slope(1000.0, 0.0, 50000.0) == -0.02


def test_compute_edge_slope_missing_value():
    assert compute_edge_slope(None, 0.0, 5000.0) is None


def test_compute_edge_slope_flat():
    assert compute_edge_slope(100.0, 100.0, 5000.0) == 0.0


def test_compute_edge_slope_zero_length():
    assert compute_edge_slope(100.0, 0.0, 0.0) is None


# --- format_slope_label ratio mode ---

def test_ratio_1_20():
    assert format_slope_label(500.0, 250.0, 5000.0) == "1/20"

def test_ratio_1_50():
    assert format_slope_label(100.0, 0.0, 5000.0) == "1/50"

def test_ratio_flat():
    assert format_slope_label(100.0, 100.0, 5000.0) == "flat"

def test_ratio_missing_start():
    assert format_slope_label(None, 0.0, 5000.0) == ""

def test_ratio_missing_end():
    assert format_slope_label(100.0, None, 5000.0) == ""

def test_ratio_missing_length():
    assert format_slope_label(100.0, 0.0, None) == ""

def test_ratio_zero_length():
    assert format_slope_label(100.0, 0.0, 0.0) == ""

def test_ratio_very_flat():
    assert format_slope_label(100.0, 99.0, 100000.0) == "flat"


def test_percent_rising():
    assert format_slope_label(0.0, 100.0, 5000.0, mode="percent") == "2.00%"

def test_percent_falling():
    assert format_slope_label(100.0, 0.0, 5000.0, mode="percent") == "-2.00%"

def test_percent_no_length():
    assert format_slope_label(100.0, 0.0, None, mode="percent") == ""


def test_decimal_mode():
    assert format_slope_label(100.0, 0.0, 5000.0, mode="decimal") == "-0.0200"

def test_decimal_no_length():
    assert format_slope_label(100.0, 0.0, None, mode="decimal") == ""


def test_z_label_basic():
    assert format_z_label(1234.0) == "z=1234mm"

def test_z_label_none():
    assert format_z_label(None) == ""

def test_z_label_zero():
    assert format_z_label(0.0) == "z=0mm"

def test_z_label_custom_prefix():
    assert format_z_label(500.0, prefix="elev=", unit="m") == "elev=500m"


def test_edge_labels_full():
    result = edge_elevation_labels(100.0, 0.0, 5000.0)
    assert result["start_z"] == "z=100mm"
    assert result["end_z"] == "z=0mm"
    assert result["slope"] == "1/50"

def test_edge_labels_missing_start():
    result = edge_elevation_labels(None, 0.0, 5000.0)
    assert result["start_z"] == ""
    assert result["slope"] == ""

def test_edge_labels_percent_mode():
    result = edge_elevation_labels(100.0, 0.0, 5000.0, mode="percent")
    assert result["slope"] == "-2.00%"
