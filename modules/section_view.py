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


@dataclass(frozen=True)
class SectionSlabPiece:
    """One rectangular part of a unified slab section, in real-world mm."""
    source_id: int
    parent_id: int
    start_mm: float
    end_mm: float
    top_elevation: float
    bottom_elevation: float
    is_stepped: bool = False
    marker_mm: float = None


@dataclass(frozen=True)
class SectionOverlapBand:
    """Horizontal overlap band between a parent slab and a stepped region."""
    parent_id: int
    child_id: int
    start_mm: float
    end_mm: float
    top_elevation: float
    bottom_elevation: float


@dataclass
class SectionSlabAssembly:
    """Unified section geometry for one parent slab and its stepped regions."""
    parent_id: int
    pieces: list = field(default_factory=list)
    overlap_bands: list = field(default_factory=list)


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


def polygon_cut_intervals(points: list, axis: str, cut_coord: float) -> list:
    """Return polygon intervals crossed by an orthogonal section line.

    ``axis == "X"`` means a horizontal cut at Y=cut_coord and returns X
    intervals. ``axis == "Y"`` means a vertical cut at X=cut_coord and
    returns Y intervals. Concave polygons may return more than one interval.
    """
    if len(points) < 3:
        return []

    projected = []
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        if axis == "X":
            along_1, fixed_1 = float(point[0]), float(point[1])
            along_2, fixed_2 = float(next_point[0]), float(next_point[1])
        else:
            along_1, fixed_1 = float(point[1]), float(point[0])
            along_2, fixed_2 = float(next_point[1]), float(next_point[0])

        # Half-open edge handling counts a vertex once and avoids duplicates.
        crosses = ((fixed_1 <= cut_coord < fixed_2) or
                   (fixed_2 <= cut_coord < fixed_1))
        if not crosses:
            continue
        ratio = (cut_coord - fixed_1) / (fixed_2 - fixed_1)
        projected.append(along_1 + ratio * (along_2 - along_1))

    projected.sort()
    intervals = []
    for index in range(0, len(projected) - 1, 2):
        start = projected[index]
        end = projected[index + 1]
        if end - start > 1e-6:
            intervals.append((start, end))
    return intervals


def _subtract_intervals(base: tuple, cuts: list) -> list:
    remaining = [base]
    for cut_start, cut_end in sorted(cuts):
        updated = []
        for start, end in remaining:
            if cut_end <= start or cut_start >= end:
                updated.append((start, end))
                continue
            if start < cut_start:
                updated.append((start, min(cut_start, end)))
            if cut_end < end:
                updated.append((max(cut_end, start), end))
        remaining = updated
    return [(start, end) for start, end in remaining if end - start > 1e-6]


def merge_section_intervals(intervals: list, tolerance: float = 1e-6) -> list:
    """Return the union of overlapping/touching section intervals.

    Structural slab pieces intentionally overlap at stepped connections. Floor
    finishes do not: they form one continuous surface over that structure.
    """
    normalized = sorted(
        (min(float(start), float(end)), max(float(start), float(end)))
        for start, end in intervals
        if abs(float(end) - float(start)) > tolerance
    )
    merged = []
    for start, end in normalized:
        if not merged or start > merged[-1][1] + tolerance:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def build_unified_slab_sections(elements: list, axis: str,
                                cut_coord: float) -> list:
    """Build unified parent/stepped-slab section assemblies.

    The stepped core replaces its parent slab. The stepped slab then extends
    into the parent on each side by ``overlap_width`` to model the connection.
    All returned pieces are intended to be rendered with one material style.
    """
    slabs = [
        element for element in elements
        if getattr(element, "element_type", None) == "slab"
        and len(getattr(element, "points", []) or []) >= 3
    ]
    children_by_parent = {}
    for slab in slabs:
        if bool(getattr(slab, "is_stepped", False)):
            parent_id = int(getattr(slab, "parent_slab_id", -1))
            children_by_parent.setdefault(parent_id, []).append(slab)

    assemblies = []
    handled_children = set()
    for parent in slabs:
        if bool(getattr(parent, "is_stepped", False)):
            continue
        parent_id = int(getattr(parent, "id", -1))
        parent_intervals = polygon_cut_intervals(parent.points, axis, cut_coord)
        if not parent_intervals:
            continue

        assembly = SectionSlabAssembly(parent_id=parent_id)
        parent_top = float(getattr(parent, "top_elevation", 0.0) or 0.0)
        parent_bottom = float(
            getattr(parent, "bottom_elevation", parent_top - float(getattr(parent, "height", 0.0) or 0.0))
        )

        child_data = []
        for child in children_by_parent.get(parent_id, []):
            child_intervals = polygon_cut_intervals(child.points, axis, cut_coord)
            for child_start, child_end in child_intervals:
                child_data.append((child, child_start, child_end))
                handled_children.add(int(getattr(child, "id", -1)))

        for parent_start, parent_end in parent_intervals:
            clipped_children = []
            for child, child_start, child_end in child_data:
                core_start = max(parent_start, child_start)
                core_end = min(parent_end, child_end)
                if core_end - core_start > 1e-6:
                    clipped_children.append((child, core_start, core_end))

            cores = [(start, end) for _, start, end in clipped_children]
            for start, end in _subtract_intervals((parent_start, parent_end), cores):
                assembly.pieces.append(SectionSlabPiece(
                    source_id=parent_id,
                    parent_id=parent_id,
                    start_mm=start,
                    end_mm=end,
                    top_elevation=parent_top,
                    bottom_elevation=parent_bottom,
                ))

            for child, core_start, core_end in clipped_children:
                child_id = int(getattr(child, "id", -1))
                child_top = float(getattr(child, "top_elevation", 0.0) or 0.0)
                child_bottom = float(
                    getattr(child, "bottom_elevation", child_top - float(getattr(child, "height", 0.0) or 0.0))
                )
                overlap = max(0.0, float(getattr(child, "overlap_width", 0.0) or 0.0))
                extended_start = max(parent_start, core_start - overlap)
                extended_end = min(parent_end, core_end + overlap)
                assembly.pieces.append(SectionSlabPiece(
                    source_id=child_id,
                    parent_id=parent_id,
                    start_mm=extended_start,
                    end_mm=extended_end,
                    top_elevation=child_top,
                    bottom_elevation=child_bottom,
                    is_stepped=True,
                    marker_mm=core_start,
                ))
                band_top = max(parent_top, child_top)
                band_bottom = min(parent_bottom, child_bottom)
                if extended_start < core_start:
                    assembly.overlap_bands.append(SectionOverlapBand(
                        parent_id, child_id, extended_start, core_start,
                        band_top, band_bottom,
                    ))
                if core_end < extended_end:
                    assembly.overlap_bands.append(SectionOverlapBand(
                        parent_id, child_id, core_end, extended_end,
                        band_top, band_bottom,
                    ))

        assemblies.append(assembly)

    # Keep orphan stepped slabs visible instead of silently dropping bad data.
    for child in slabs:
        child_id = int(getattr(child, "id", -1))
        if not bool(getattr(child, "is_stepped", False)) or child_id in handled_children:
            continue
        intervals = polygon_cut_intervals(child.points, axis, cut_coord)
        if not intervals:
            continue
        top = float(getattr(child, "top_elevation", 0.0) or 0.0)
        bottom = float(
            getattr(child, "bottom_elevation", top - float(getattr(child, "height", 0.0) or 0.0))
        )
        assembly = SectionSlabAssembly(parent_id=int(getattr(child, "parent_slab_id", -1)))
        for start, end in intervals:
            assembly.pieces.append(SectionSlabPiece(
                child_id, assembly.parent_id, start, end, top, bottom, True,
            ))
        assemblies.append(assembly)

    return assemblies


def format_slab_label(top_elevation: float, thickness: float, sl_zero: float = 0.0) -> str:
    """Canvas label for a slab: 'SL±0 / t150'."""
    elev_str = format_elevation_label("SL", top_elevation, sl_zero)
    return "{} / t{:g}".format(elev_str, thickness)


def format_beam_label(bottom_elevation: float, width: float, height: float,
                      sl_zero: float = 0.0) -> str:
    """Canvas label for a beam: 'SL-500 / 300×600'."""
    elev_str = format_elevation_label("SL", bottom_elevation, sl_zero)
    return "{} / {:g}×{:g}".format(elev_str, width, height)


def format_ceiling_ch(ceiling_bottom: float, fl_elevation: float) -> str:
    """Canvas label for ceiling: 'CH=2360'."""
    ch = compute_ch(fl_elevation, ceiling_bottom)
    return "CH={:g}".format(ch)
