from __future__ import annotations

import math


def compute_fl(sl: float, finish_thickness: float) -> float:
    """Finish Level = Structural Level + finish layer thickness."""
    return float(sl) + float(finish_thickness)


def compute_ch(ceiling_bottom: float, fl: float) -> float:
    """Clear Height = ceiling bottom elevation - Finish Level."""
    return float(ceiling_bottom) - float(fl)


def _segment_intersects_rect(p1: tuple[float, float], p2: tuple[float, float],
                              xs: list[float], ys: list[float]) -> bool:
    """Check if segment p1-p2 intersects the bounding box defined by xs, ys."""
    if not xs or not ys:
        return False
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    ax, ay = float(p1[0]), float(p1[1])
    bx, by = float(p2[0]), float(p2[1])

    def _on_left(px, py): return (bx - ax) * (py - ay) - (by - ay) * (px - ax)

    corners = [(left, top), (right, top), (right, bottom), (left, bottom)]
    signs = [_on_left(cx, cy) for cx, cy in corners]
    if all(s > 0 for s in signs) or all(s < 0 for s in signs):
        return False

    # Check if the segment crosses the rectangle's x and y extents
    min_x_seg, max_x_seg = min(ax, bx), max(ax, bx)
    min_y_seg, max_y_seg = min(ay, by), max(ay, by)
    if max_x_seg < left or min_x_seg > right:
        return False
    if max_y_seg < top or min_y_seg > bottom:
        return False
    return True


def elements_intersect_cut_line(elements, p1: tuple[float, float], p2: tuple[float, float]) -> list:
    """Return elements whose bounding box intersects the cut line segment p1-p2."""
    result = []
    for element in elements:
        points = list(getattr(element, "points", []) or [])
        if len(points) < 3:
            continue
        xs = [float(pt[0]) for pt in points]
        ys = [float(pt[1]) for pt in points]
        if _segment_intersects_rect(p1, p2, xs, ys):
            result.append(element)
    return result


def sort_elements_by_elevation(elements) -> list:
    """Sort elements by bottom_elevation ascending (lowest first)."""
    return sorted(
        elements,
        key=lambda e: float(getattr(e, "bottom_elevation", 0.0) or 0.0),
    )
