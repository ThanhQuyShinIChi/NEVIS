"""Tests for modules/structural_input.py — no Qt dependency."""
import pytest
from modules.structural_input import validate_dimension, validate_positive_dimension, validate_element_dimensions


# --- validate_dimension ---

def test_valid_zero():
    v, err = validate_dimension(0, "W")
    assert v == 0.0 and err == ""

def test_valid_positive():
    v, err = validate_dimension("500", "W")
    assert v == 500.0 and err == ""

def test_invalid_negative():
    v, err = validate_dimension(-1, "W")
    assert err != ""

def test_invalid_string():
    v, err = validate_dimension("abc", "W")
    assert v == 0.0 and err != ""

def test_invalid_none():
    v, err = validate_dimension(None, "W")
    assert err != ""

def test_exceeds_max():
    v, err = validate_dimension(100000, "W")
    assert err != ""

def test_max_exact():
    v, err = validate_dimension(99999.0, "W")
    assert err == ""


# --- validate_positive_dimension ---

def test_positive_zero_fails():
    v, err = validate_positive_dimension(0, "H")
    assert err != ""

def test_positive_valid():
    v, err = validate_positive_dimension(200, "H")
    assert v == 200.0 and err == ""


# --- validate_element_dimensions ---

def test_element_dims_all_valid():
    r = validate_element_dimensions(w=300, l=600, h=150, c=0)
    assert r["errors"] == {}
    assert r["w"] == 300.0

def test_element_dims_partial():
    r = validate_element_dimensions(w=100)
    assert "w" in r
    assert "l" not in r

def test_element_dims_error_collected():
    r = validate_element_dimensions(w=-1, l=500)
    assert "w" in r["errors"]
    assert "l" not in r["errors"]

def test_element_dims_c_zero_ok():
    r = validate_element_dimensions(c=0)
    assert r["errors"] == {}
