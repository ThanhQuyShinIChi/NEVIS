from __future__ import annotations

import pytest

from modules.structural_input import rect_from_center_wl, validate_dimension


@pytest.mark.parametrize(
    ("value", "name", "expected"),
    [
        ("125.5", "W", 125.5),
        (1, "L", 1.0),
        (99999, "H", 99999.0),
        (0, "C", 0.0),
        ("25", "C", 25.0),
    ],
)
def test_validate_dimension_accepts_valid_values(value, name: str, expected: float) -> None:
    number, error = validate_dimension(value, name)

    assert number == expected
    assert error == ""


@pytest.mark.parametrize(
    ("value", "name"),
    [
        ("", "W"),
        ("abc", "L"),
        (0, "H"),
        (-1, "W"),
        (-0.1, "C"),
        (100000, "L"),
        (100000, "C"),
        (float("nan"), "W"),
        (float("inf"), "H"),
    ],
)
def test_validate_dimension_rejects_invalid_values(value, name: str) -> None:
    _, error = validate_dimension(value, name)

    assert error
    assert name in error


def test_rect_from_center_wl_returns_clockwise_screen_points() -> None:
    assert rect_from_center_wl(100.0, 200.0, 40.0, 60.0) == [
        (80.0, 170.0),
        (120.0, 170.0),
        (120.0, 230.0),
        (80.0, 230.0),
    ]


def test_rect_from_center_wl_supports_float_values() -> None:
    assert rect_from_center_wl(0.5, -0.5, 1.0, 3.0) == [
        (0.0, -2.0),
        (1.0, -2.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]
