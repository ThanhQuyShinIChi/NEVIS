from __future__ import annotations

from modules.stepped_slab import (
    compute_stepped_slab_elevation,
    validate_stepped_slab_bounds,
)
from modules.structural_element import (
    StructuralElement,
    structural_element_from_dict,
    structural_element_to_dict,
)


def slab(element_id: int, points) -> StructuralElement:
    return StructuralElement(id=element_id, element_type="slab", points=points, height=150.0)


def test_validate_stepped_slab_bounds_accepts_child_inside_parent() -> None:
    parent = slab(1, [(0, 0), (1000, 0), (1000, 800), (0, 800)])
    child = slab(2, [(100, 200), (500, 200), (500, 600), (100, 600)])

    assert validate_stepped_slab_bounds(parent, child)


def test_validate_stepped_slab_bounds_accepts_shared_boundary() -> None:
    parent = slab(1, [(0, 0), (1000, 0), (1000, 800), (0, 800)])
    child = slab(2, [(0, 0), (500, 0), (500, 400), (0, 400)])

    assert validate_stepped_slab_bounds(parent, child)


def test_validate_stepped_slab_bounds_rejects_child_outside_parent() -> None:
    parent = slab(1, [(0, 0), (1000, 0), (1000, 800), (0, 800)])
    child = slab(2, [(900, 200), (1100, 200), (1100, 600), (900, 600)])

    assert not validate_stepped_slab_bounds(parent, child)
    assert not validate_stepped_slab_bounds(parent, slab(3, []))


def test_compute_stepped_slab_elevation_subtracts_downward_offset() -> None:
    assert compute_stepped_slab_elevation(0.0, 200.0) == -200.0
    assert compute_stepped_slab_elevation(3000.0, 150.0) == 2850.0


def test_stepped_slab_round_trip_preserves_parent_and_elevations() -> None:
    original = StructuralElement(
        id=12,
        element_type="slab",
        label="Stepped",
        points=[(100, 100), (500, 100), (500, 400), (100, 400)],
        width=400.0,
        length=300.0,
        height=180.0,
        top_elevation=-200.0,
        is_stepped=True,
        parent_slab_id=4,
        overlap_width=250.0,
    )

    restored = structural_element_from_dict(structural_element_to_dict(original))

    assert restored == original
    assert restored.is_stepped is True
    assert restored.parent_slab_id == 4
    assert restored.overlap_width == 250.0
    assert restored.top_elevation == -200.0
    assert restored.bottom_elevation == -380.0
