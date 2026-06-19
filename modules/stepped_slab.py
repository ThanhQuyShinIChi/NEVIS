from __future__ import annotations

from modules.structural_element import StructuralElement


def validate_stepped_slab_bounds(parent: StructuralElement, child: StructuralElement) -> bool:
    """Return True when every child point is inside the parent's axis-aligned bounds."""
    if len(parent.points) < 3 or len(child.points) < 3:
        return False
    parent_x = [float(point[0]) for point in parent.points]
    parent_y = [float(point[1]) for point in parent.points]
    left, right = min(parent_x), max(parent_x)
    top, bottom = min(parent_y), max(parent_y)
    return all(
        left <= float(x) <= right and top <= float(y) <= bottom
        for x, y in child.points
    )


def compute_stepped_slab_elevation(sl_elevation: float, offset_mm: float) -> float:
    """Compute a lowered slab elevation; a positive offset is downward from SL."""
    return float(sl_elevation) - float(offset_mm)
