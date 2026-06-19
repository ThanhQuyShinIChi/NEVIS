from __future__ import annotations

import pytest

from modules.structural_element import (
    StructuralElement,
    structural_element_from_dict,
    structural_element_to_dict,
)


@pytest.mark.parametrize(
    "element_type",
    ["slab", "beam", "column", "wall_rc", "wall_lgs", "ceiling"],
)
def test_round_trip_for_each_element_type(element_type: str) -> None:
    element = StructuralElement(
        id=7,
        element_type=element_type,
        label="A-7",
        points=[(10.0, 20.0), (310.0, 20.0), (310.0, 420.0), (10.0, 420.0)],
        width=300.0,
        length=400.0,
        height=150.0,
        arc_radius=25.0,
        top_elevation=1200.0,
        stud_spacing=455.0,
        stud_width=100.0,
        board_thickness=15.0,
        board_layers=2,
        is_stepped=element_type == "slab",
        parent_slab_id=3,
        overlap_width=200.0,
    )

    restored = structural_element_from_dict(structural_element_to_dict(element))

    assert restored == element
    assert restored.points == element.points
    assert all(isinstance(point, tuple) for point in restored.points)


def test_missing_fields_use_safe_defaults() -> None:
    restored = structural_element_from_dict({"id": 2, "element_type": "beam"})

    assert restored == StructuralElement(id=2, element_type="beam")
    assert restored.points == []
    assert restored.stud_spacing == 303.0
    assert restored.stud_width == 65.0
    assert restored.board_thickness == 12.5
    assert restored.board_layers == 1
    assert restored.parent_slab_id == -1


def test_bottom_elevation_is_computed_from_top_and_height() -> None:
    element = StructuralElement(
        id=1,
        element_type="slab",
        height=180.0,
        top_elevation=-20.0,
        bottom_elevation=9999.0,
    )

    assert element.bottom_elevation == -200.0
    restored = structural_element_from_dict(
        {"id": 1, "element_type": "slab", "height": 180, "top_elevation": -20, "bottom_elevation": 5}
    )
    assert restored.bottom_elevation == -200.0


def test_invalid_values_fall_back_without_crashing() -> None:
    restored = structural_element_from_dict(
        {"id": None, "points": [[1, 2], ["bad", 3], None], "height": "", "stud_spacing": None}
    )

    assert restored.id == 0
    assert restored.element_type == ""
    assert restored.points == [(1.0, 2.0)]
    assert restored.height == 0.0
    assert restored.stud_spacing == 303.0
