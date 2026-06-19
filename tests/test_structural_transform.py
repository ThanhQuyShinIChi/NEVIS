from __future__ import annotations

import pytest

from modules.structural_element import StructuralElement
from modules.structural_transform import move_element, resize_element


def rectangle() -> StructuralElement:
    return StructuralElement(
        id=1,
        element_type="beam",
        points=[(10.0, 20.0), (110.0, 20.0), (110.0, 220.0), (10.0, 220.0)],
        width=100.0,
        length=200.0,
        height=300.0,
    )


def test_move_element_offsets_all_points_without_mutating_original() -> None:
    original = rectangle()

    moved = move_element(original, 25.0, -10.0)

    assert moved.points == [(35.0, 10.0), (135.0, 10.0), (135.0, 210.0), (35.0, 210.0)]
    assert moved.width == 100.0
    assert moved.length == 200.0
    assert original.points[0] == (10.0, 20.0)


@pytest.mark.parametrize(
    ("handle", "new_pos", "expected_points", "expected_w", "expected_l"),
    [
        ("nw", (-10.0, 0.0), [(-10.0, 0.0), (110.0, 0.0), (110.0, 220.0), (-10.0, 220.0)], 120.0, 220.0),
        ("e", (160.0, 999.0), [(10.0, 20.0), (160.0, 20.0), (160.0, 220.0), (10.0, 220.0)], 150.0, 200.0),
        ("s", (999.0, 250.0), [(10.0, 20.0), (110.0, 20.0), (110.0, 250.0), (10.0, 250.0)], 100.0, 230.0),
        ("se", (140.0, 260.0), [(10.0, 20.0), (140.0, 20.0), (140.0, 260.0), (10.0, 260.0)], 130.0, 240.0),
    ],
)
def test_resize_element_updates_points_width_and_length(
    handle: str,
    new_pos,
    expected_points,
    expected_w: float,
    expected_l: float,
) -> None:
    resized = resize_element(rectangle(), handle, new_pos)

    assert resized.points == expected_points
    assert resized.width == expected_w
    assert resized.length == expected_l
    assert resized.height == 300.0


def test_resize_element_normalizes_when_handle_crosses_opposite_edge() -> None:
    resized = resize_element(rectangle(), "nw", (150.0, 260.0))

    assert resized.points == [(110.0, 220.0), (150.0, 220.0), (150.0, 260.0), (110.0, 260.0)]
    assert resized.width == 40.0
    assert resized.length == 40.0


def test_resize_element_rejects_unknown_handle() -> None:
    with pytest.raises(ValueError, match="Unknown resize handle"):
        resize_element(rectangle(), "center", (0.0, 0.0))


def test_resize_element_accepts_long_handle_names() -> None:
    resized = resize_element(rectangle(), "bottom_right", (150.0, 260.0))

    assert resized.width == 140.0
    assert resized.length == 240.0
