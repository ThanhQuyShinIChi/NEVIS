"""Section view elevation labels (GL/SL/FL/CH) — no Qt dependency."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ElevationMarker:
    """One elevation marker line in a section view."""
    label: str          # "GL", "SL", "FL", "CH", or custom
    elevation_mm: float # relative to SL=0
    color: str = "#000000"
    line_style: str = "solid"  # "solid" | "dashed"


# Standard Japanese construction elevation relationships
# GL: Ground Level (mặt đất)
# SL: Structural Level = ±0 (mặt trên sàn BT thô)
# FL: Finish Level = SL + hoàn thiện (thường 30-50mm)
# CH: Clear Height = from FL to bottom of ceiling (軽天)

def compute_fl(sl_elevation: float, finish_thickness_mm: float = 40.0) -> float:
    """FL = SL + finish_thickness."""
    return sl_elevation + finish_thickness_mm


def compute_ch(fl_elevation: float, ceiling_bottom_elevation: float) -> float:
    """CH = ceiling_bottom_elevation - FL (positive means ceiling is above FL)."""
    return ceiling_bottom_elevation - fl_elevation


def format_elevation_label(label: str, elevation_mm: float, sl_zero: float = 0.0) -> str:
    """Format elevation as 'SL±0', 'SL+xxx', 'SL-xxx' etc."""
    delta = elevation_mm - sl_zero
    if abs(delta) < 0.5:
        return "SL±0"
    elif delta > 0:
        return "SL+{}".format(int(round(delta)))
    else:
        return "SL{}".format(int(round(delta)))


def build_standard_markers(gl_mm: float, sl_mm: float = 0.0,
                            finish_thickness: float = 40.0,
                            ceiling_bottom: float = None,
                            ceiling_finish: float = 12.5) -> list:
    """Build standard GL/SL/FL/CH marker list for a section view."""
    markers = [
        ElevationMarker("GL", gl_mm, color="#8B4513", line_style="solid"),
        ElevationMarker("SL±0", sl_mm, color="#000000", line_style="solid"),
    ]
    fl = compute_fl(sl_mm, finish_thickness)
    markers.append(ElevationMarker("FL", fl, color="#0000CC", line_style="dashed"))
    if ceiling_bottom is not None:
        ch = compute_ch(fl, ceiling_bottom - ceiling_finish)
        markers.append(ElevationMarker(
            "CH={:.0f}".format(ch), ceiling_bottom - ceiling_finish,
            color="#006600", line_style="dashed",
        ))
    return markers


def section_marker_to_dict(m: ElevationMarker) -> dict:
    return {"label": m.label, "elevation_mm": m.elevation_mm,
            "color": m.color, "line_style": m.line_style}


def section_marker_from_dict(d: dict) -> ElevationMarker:
    return ElevationMarker(
        label=str(d.get("label", "")),
        elevation_mm=float(d.get("elevation_mm", 0.0)),
        color=str(d.get("color", "#000000")),
        line_style=str(d.get("line_style", "solid")),
    )


def elements_intersect_cut_line(elements: list, cut_x: float) -> list:
    """Return elements whose bounding box crosses the vertical cut line at cut_x."""
    result = []
    for e in elements:
        if not e.points:
            continue
        xs = [p[0] for p in e.points]
        if min(xs) <= cut_x <= max(xs):
            result.append(e)
    return result


def sort_elements_by_elevation(elements: list) -> list:
    """Return elements sorted by top_elevation descending (highest first)."""
    return sorted(elements, key=lambda e: e.top_elevation, reverse=True)
