"""Stepped slab (sàn giật cấp) logic — no Qt dependency."""
from __future__ import annotations
from modules.structural_element import StructuralElement
from modules.structural_geometry import rect_bounds, rect_contains


def validate_stepped_slab_bounds(parent: StructuralElement, child: StructuralElement) -> bool:
    """Return True if child slab is fully within parent slab bounds."""
    if not parent.points or not child.points:
        return False
    return rect_contains(parent.points, child.points)


def compute_stepped_slab_elevation(sl_elevation: float, offset_mm: float) -> float:
    """Return top_elevation for a stepped slab that is offset_mm below the given sl_elevation."""
    return sl_elevation - abs(offset_mm)


def stepped_slab_overlap_region(parent: StructuralElement, child: StructuralElement,
                                 overlap_width: float) -> list:
    """Return bounding box points of the overlap strip (child edge expanded by overlap_width inward).

    Returns 4 corner points or [] if child has no points.
    """
    if not child.points:
        return []
    ix0, iy0, ix1, iy1 = rect_bounds(child.points)
    # expand inward (shrink) by overlap_width on all sides
    ox0 = ix0 + overlap_width
    oy0 = iy0 + overlap_width
    ox1 = ix1 - overlap_width
    oy1 = iy1 - overlap_width
    if ox0 >= ox1 or oy0 >= oy1:
        return []
    return [(ox0, oy0), (ox1, oy0), (ox1, oy1), (ox0, oy1)]
