"""Move and resize StructuralElement — no Qt dependency."""
from __future__ import annotations
from modules.structural_element import StructuralElement, structural_element_to_dict, structural_element_from_dict


def move_element(elem: StructuralElement, dx: float, dy: float) -> StructuralElement:
    """Return a copy of elem with all points translated by (dx, dy)."""
    d = structural_element_to_dict(elem)
    d["points"] = [[p[0] + dx, p[1] + dy] for p in elem.points]
    return structural_element_from_dict(d)


def resize_element(elem: StructuralElement, handle: str, new_pos: tuple) -> StructuralElement:
    """Resize element by moving a named handle. handle: 'tl','tr','br','bl','t','r','b','l'."""
    if not elem.points or len(elem.points) < 4:
        return elem
    pts = list(elem.points)
    x0 = min(p[0] for p in pts)
    y0 = min(p[1] for p in pts)
    x1 = max(p[0] for p in pts)
    y1 = max(p[1] for p in pts)
    nx, ny = new_pos
    if handle == "tl":
        x0, y0 = nx, ny
    elif handle == "tr":
        x1, y0 = nx, ny
    elif handle == "br":
        x1, y1 = nx, ny
    elif handle == "bl":
        x0, y1 = nx, ny
    elif handle == "t":
        y0 = ny
    elif handle == "b":
        y1 = ny
    elif handle == "l":
        x0 = nx
    elif handle == "r":
        x1 = nx
    # Ensure min < max
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    new_pts = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    d = structural_element_to_dict(elem)
    d["points"] = new_pts
    w = abs(x1 - x0)
    l = abs(y1 - y0)
    d["width"] = w
    d["length"] = l
    return structural_element_from_dict(d)


def element_handle_positions(elem: StructuralElement) -> dict:
    """Return dict of handle_name -> (x, y) for an element with 4 corner points."""
    if not elem.points or len(elem.points) < 4:
        return {}
    x0 = min(p[0] for p in elem.points)
    y0 = min(p[1] for p in elem.points)
    x1 = max(p[0] for p in elem.points)
    y1 = max(p[1] for p in elem.points)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return {
        "tl": (x0, y0), "t": (mx, y0), "tr": (x1, y0),
        "l": (x0, my),                   "r": (x1, my),
        "bl": (x0, y1), "b": (mx, y1), "br": (x1, y1),
    }
