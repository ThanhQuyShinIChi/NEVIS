from __future__ import annotations

from dataclasses import replace

from modules.structural_element import StructuralElement
from modules.structural_geometry import Point, rect_from_two_points


VALID_RESIZE_HANDLES = {"nw", "n", "ne", "e", "se", "s", "sw", "w"}
HANDLE_ALIASES = {
    "top_left": "nw",
    "top": "n",
    "top_right": "ne",
    "right": "e",
    "bottom_right": "se",
    "bottom": "s",
    "bottom_left": "sw",
    "left": "w",
}


def move_element(element: StructuralElement, dx: float, dy: float) -> StructuralElement:
    offset_x, offset_y = float(dx), float(dy)
    return replace(
        element,
        points=[(float(x) + offset_x, float(y) + offset_y) for x, y in element.points],
    )


def resize_element(element: StructuralElement, handle: str, new_pos: Point) -> StructuralElement:
    handle = str(handle).lower()
    handle = HANDLE_ALIASES.get(handle, handle)
    if handle not in VALID_RESIZE_HANDLES:
        raise ValueError(f"Unknown resize handle: {handle}")
    if not element.points:
        return replace(element)

    xs = [float(point[0]) for point in element.points]
    ys = [float(point[1]) for point in element.points]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    new_x, new_y = float(new_pos[0]), float(new_pos[1])

    if "w" in handle:
        left = new_x
    elif "e" in handle:
        right = new_x
    if "n" in handle:
        top = new_y
    elif "s" in handle:
        bottom = new_y

    points = rect_from_two_points((left, top), (right, bottom))
    return replace(
        element,
        points=points,
        width=abs(right - left),
        length=abs(bottom - top),
    )
