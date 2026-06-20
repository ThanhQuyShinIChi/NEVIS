"""2.5D clash detection — no Qt dependency."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ClashResult:
    pipe_id: int
    element_id: int
    element_type: str       # "slab", "beam", "column", "wall_rc", "wall_lgs", "ceiling"
    clash_type: str         # "penetrate" | "too_close"
    overlap_mm: float       # >0 xuyên vào phần tử; <0 quá gần nhưng chưa chạm


def point_in_polygon(px: float, py: float, polygon: list) -> bool:
    """Ray casting — True nếu (px, py) nằm trong polygon."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def segment_intersects_polygon(p1: tuple, p2: tuple, polygon: list) -> bool:
    """True nếu đoạn p1→p2 có ít nhất một điểm nằm trong polygon."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = (dx * dx + dy * dy) ** 0.5
    steps = max(2, int(length // 100) + 2)
    for k in range(steps + 1):
        t = k / steps
        px = p1[0] + t * dx
        py = p1[1] + t * dy
        if point_in_polygon(px, py, polygon):
            return True
    return False


def check_elevation_clash(
    pipe_z: float,
    elem_bottom: float,
    elem_top: float,
    clearance_mm: float = 50.0,
) -> tuple[bool, float]:
    """
    Kiểm tra Z ống có xung đột với dải cao độ phần tử không.
    Returns: (is_clash, overlap_mm)
      overlap_mm > 0: ống xuyên vào phần tử
      overlap_mm < 0: ống gần phần tử nhưng chưa chạm (< clearance_mm)
    """
    if elem_bottom <= pipe_z <= elem_top:
        overlap = min(pipe_z - elem_bottom, elem_top - pipe_z)
        return True, overlap
    if pipe_z < elem_bottom:
        gap = elem_bottom - pipe_z
    else:
        gap = pipe_z - elem_top
    if gap < clearance_mm:
        return True, -gap
    return False, gap


def find_clashes(
    pipes: list,
    elements: list,
    clearance_mm: float = 50.0,
) -> list[ClashResult]:
    """
    Kiểm tra tất cả pipe segments vs tất cả structural elements.

    pipes: list of objects với attrs: id, z_elevation, points (list of (x,y))
    elements: list of StructuralElement với attrs:
              id, element_type, points, top_elevation, bottom_elevation
    """
    results: list[ClashResult] = []
    for pipe in pipes:
        pts = getattr(pipe, "points", None)
        if not pts or len(pts) < 2:
            continue
        pipe_z = getattr(pipe, "z_elevation", 0.0)
        for elem in elements:
            elem_pts = getattr(elem, "points", None)
            if not elem_pts or len(elem_pts) < 3:
                continue
            elem_top = getattr(elem, "top_elevation", 0.0)
            elem_bottom = getattr(elem, "bottom_elevation", 0.0)

            xy_clash = False
            for i in range(len(pts) - 1):
                if segment_intersects_polygon(pts[i], pts[i + 1], elem_pts):
                    xy_clash = True
                    break
            if not xy_clash:
                continue

            is_clash, overlap = check_elevation_clash(
                pipe_z, elem_bottom, elem_top, clearance_mm
            )
            if is_clash:
                clash_type = "penetrate" if overlap >= 0 else "too_close"
                results.append(
                    ClashResult(
                        pipe_id=getattr(pipe, "id", 0),
                        element_id=getattr(elem, "id", 0),
                        element_type=getattr(elem, "element_type", ""),
                        clash_type=clash_type,
                        overlap_mm=overlap,
                    )
                )
    return results
