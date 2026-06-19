"""Data model for structural building elements (slab, beam, column, wall, ceiling).

No UI or Qt dependency — pure data + serialize/deserialize.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StructuralElement:
    id: int
    element_type: str  # "slab"|"beam"|"column"|"wall_rc"|"wall_lgs"|"ceiling"
    label: str = ""

    # Geometry: list of (x, y) in canvas mm coordinates
    # Rectangle: [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    points: list = field(default_factory=list)

    # Dimensions (mm)
    width: float = 0.0       # W
    length: float = 0.0      # L
    height: float = 0.0      # H — thickness for slab/wall, height for column/beam
    arc_radius: float = 0.0  # C — 0 means no arc

    # Elevation relative to SL=0 (mm)
    top_elevation: float = 0.0
    bottom_elevation: float = 0.0  # = top_elevation - height

    # LGS partition wall (wall_lgs) specific
    stud_spacing: float = 303.0    # mm, Japanese standard: 303 (1尺) or 455 (1.5尺)
    stud_width: float = 65.0       # mm, 65 (standard) or 100 (sound insulation)
    board_thickness: float = 12.5  # mm, gypsum board thickness
    board_layers: int = 1          # number of gypsum board layers per side

    # Stepped slab (sàn giật cấp)
    is_stepped: bool = False
    parent_slab_id: int = -1    # id of parent slab, -1 = none
    overlap_width: float = 0.0  # mm, overlap with parent slab edge


VALID_TYPES = {"slab", "beam", "column", "wall_rc", "wall_lgs", "ceiling"}

_DEFAULTS = StructuralElement(id=0, element_type="slab")


def structural_element_to_dict(e: StructuralElement) -> dict:
    return {
        "id": e.id,
        "element_type": e.element_type,
        "label": e.label,
        "points": [list(p) for p in e.points],
        "width": e.width,
        "length": e.length,
        "height": e.height,
        "arc_radius": e.arc_radius,
        "top_elevation": e.top_elevation,
        "bottom_elevation": e.bottom_elevation,
        "stud_spacing": e.stud_spacing,
        "stud_width": e.stud_width,
        "board_thickness": e.board_thickness,
        "board_layers": e.board_layers,
        "is_stepped": e.is_stepped,
        "parent_slab_id": e.parent_slab_id,
        "overlap_width": e.overlap_width,
    }


def structural_element_from_dict(d: dict) -> StructuralElement:
    """Deserialize from dict. Missing fields use safe defaults."""
    eid = int(d.get("id", 0))
    etype = str(d.get("element_type", "slab"))
    if etype not in VALID_TYPES:
        etype = "slab"

    raw_points = d.get("points", [])
    points = [tuple(p) for p in raw_points if len(p) >= 2]

    def _f(key: str, default: float) -> float:
        try:
            return float(d[key])
        except (KeyError, TypeError, ValueError):
            return default

    def _i(key: str, default: int) -> int:
        try:
            return int(d[key])
        except (KeyError, TypeError, ValueError):
            return default

    def _b(key: str, default: bool) -> bool:
        try:
            return bool(d[key])
        except (KeyError, TypeError, ValueError):
            return default

    return StructuralElement(
        id=eid,
        element_type=etype,
        label=str(d.get("label", "")),
        points=points,
        width=_f("width", 0.0),
        length=_f("length", 0.0),
        height=_f("height", 0.0),
        arc_radius=_f("arc_radius", 0.0),
        top_elevation=_f("top_elevation", 0.0),
        bottom_elevation=_f("bottom_elevation", 0.0),
        stud_spacing=_f("stud_spacing", 303.0),
        stud_width=_f("stud_width", 65.0),
        board_thickness=_f("board_thickness", 12.5),
        board_layers=_i("board_layers", 1),
        is_stepped=_b("is_stepped", False),
        parent_slab_id=_i("parent_slab_id", -1),
        overlap_width=_f("overlap_width", 0.0),
    )
