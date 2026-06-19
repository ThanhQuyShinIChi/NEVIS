"""Input validation for structural element dimensions — no Qt dependency."""
from __future__ import annotations
from modules.structural_geometry import rect_from_center_wl  # re-export for Nevis_no_ui


_MAX_DIM = 99999.0


def validate_dimension(value, name: str = "value") -> tuple:
    """Validate a dimension field. Returns (float, error_str). error_str is '' on success."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return (0.0, "{} must be a number".format(name))
    if v < 0:
        return (0.0, "{} must be >= 0".format(name))
    if v > _MAX_DIM:
        return (0.0, "{} must be <= {} mm".format(name, int(_MAX_DIM)))
    return (v, "")


def validate_positive_dimension(value, name: str = "value") -> tuple:
    """Like validate_dimension but requires value > 0."""
    v, err = validate_dimension(value, name)
    if err:
        return (v, err)
    if v <= 0:
        return (0.0, "{} must be > 0".format(name))
    return (v, "")


def validate_element_dimensions(w=None, l=None, h=None, c=None) -> dict:
    """Validate W/L/H/C fields. Returns dict with 'errors' key and parsed values."""
    result = {}
    errors = {}
    for key, val, positive in [("w", w, True), ("l", l, True), ("h", h, True), ("c", c, False)]:
        if val is None:
            continue
        fn = validate_positive_dimension if positive else validate_dimension
        parsed, err = fn(val, key.upper())
        result[key] = parsed
        if err:
            errors[key] = err
    result["errors"] = errors
    return result
