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

    # Floor finish (lớp hoàn thiện sàn)
    # finish_layers: list of {"name": str, "thickness": float}  — ordered bottom→top
    # finish_thickness_mm: fallback total when finish_layers is empty
    # Use get_finish_thickness(elem) to always get the correct total.
    finish_layers: list = field(default_factory=list)
    finish_thickness_mm: float = 0.0

    # Wall finish layers (lớp hoàn thiện tường)
    # inner: layers from structural face going inward (toward room interior), ordered face→room
    # outer: layers from structural face going outward (toward outside/corridor/other room)
    # Each layer: {"name": str, "thickness": float, "material_type": str}
    # material_type: "insulation_ur"|"insulation_gw"|"gl"|"gypsum"|"gypsum_fire"
    #                "gypsum_hard"|"gypsum_wet"|"air_gap"|"lgs_frame"
    # wall_rc_thickness: RC structural body thickness (mm) — Japan standard 180mm
    # lgs_is_staggered: True for 千鳥配置 (W-01 界壁), frame_width = stud_width + 12
    #                   False for single-row LGS, frame_width = stud_width + 2 (tracks)
    wall_finish_inner: list = field(default_factory=list)
    wall_finish_outer: list = field(default_factory=list)
    wall_finish_type_code: str = ""
    wall_rc_thickness: float = 180.0
    lgs_is_staggered: bool = False


VALID_TYPES = {"slab", "beam", "column", "wall_rc", "wall_lgs", "ceiling"}


def get_finish_thickness(e: StructuralElement) -> float:
    """Total floor-finish thickness: sum of layers if any, else finish_thickness_mm."""
    if e.finish_layers:
        return sum(float(lay.get("thickness", 0.0)) for lay in e.finish_layers)
    return float(e.finish_thickness_mm)


def get_wall_frame_width(e: StructuralElement) -> float:
    """LGS effective frame width (mm).
    Single-row: stud_width + 2mm (tracks).  千鳥: stud_width + 12mm."""
    if e.element_type != "wall_lgs":
        return 0.0
    extra = 12.0 if e.lgs_is_staggered else 2.0
    return float(e.stud_width) + extra


def get_wall_total_width(e: StructuralElement) -> float:
    """Total wall width = structural body + all finish layers (mm).
    LGS: frame + inner_finish + outer_finish.
    RC:  wall_rc_thickness + inner_finish + outer_finish."""
    inner = sum(float(l.get("thickness", 0.0)) for l in e.wall_finish_inner)
    outer = sum(float(l.get("thickness", 0.0)) for l in e.wall_finish_outer)
    if e.element_type == "wall_lgs":
        return get_wall_frame_width(e) + inner + outer
    if e.element_type == "wall_rc":
        return float(e.wall_rc_thickness) + inner + outer
    return float(e.width)

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
        "finish_layers": list(e.finish_layers),
        "finish_thickness_mm": e.finish_thickness_mm,
        "wall_finish_inner": list(e.wall_finish_inner),
        "wall_finish_outer": list(e.wall_finish_outer),
        "wall_finish_type_code": e.wall_finish_type_code,
        "wall_rc_thickness": e.wall_rc_thickness,
        "lgs_is_staggered": e.lgs_is_staggered,
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
        finish_layers=[
            {"name": str(lay.get("name", "")), "thickness": float(lay.get("thickness", 0.0))}
            for lay in d.get("finish_layers", [])
            if isinstance(lay, dict)
        ],
        finish_thickness_mm=_f("finish_thickness_mm", 0.0),
        wall_finish_inner=[
            {"name": str(l.get("name", "")), "thickness": float(l.get("thickness", 0.0)),
             "material_type": str(l.get("material_type", "gypsum"))}
            for l in d.get("wall_finish_inner", []) if isinstance(l, dict)
        ],
        wall_finish_outer=[
            {"name": str(l.get("name", "")), "thickness": float(l.get("thickness", 0.0)),
             "material_type": str(l.get("material_type", "gypsum"))}
            for l in d.get("wall_finish_outer", []) if isinstance(l, dict)
        ],
        wall_finish_type_code=str(d.get("wall_finish_type_code", "")),
        wall_rc_thickness=_f("wall_rc_thickness", 180.0),
        lgs_is_staggered=_b("lgs_is_staggered", False),
    )
