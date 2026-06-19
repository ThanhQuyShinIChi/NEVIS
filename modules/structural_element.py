from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any


@dataclass
class StructuralElement:
    id: int
    element_type: str
    label: str = ""
    points: list[tuple[float, float]] = field(default_factory=list)
    width: float = 0.0
    length: float = 0.0
    height: float = 0.0
    arc_radius: float = 0.0
    top_elevation: float = 0.0
    bottom_elevation: float = 0.0
    stud_spacing: float = 303.0
    stud_width: float = 65.0
    board_thickness: float = 12.5
    board_layers: int = 1
    is_stepped: bool = False
    parent_slab_id: int = -1
    overlap_width: float = 0.0

    def __post_init__(self) -> None:
        self.bottom_elevation = self.top_elevation - self.height


def structural_element_to_dict(element: StructuralElement) -> dict[str, Any]:
    return {
        item.name: [list(point) for point in value] if item.name == "points" else value
        for item in fields(element)
        for value in (getattr(element, item.name),)
    }


def _float_value(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _points_value(value: Any) -> list[tuple[float, float]]:
    if not isinstance(value, (list, tuple)):
        return []
    points: list[tuple[float, float]] = []
    for point in value:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        try:
            points.append((float(point[0]), float(point[1])))
        except (TypeError, ValueError):
            continue
    return points


def structural_element_from_dict(data: dict[str, Any]) -> StructuralElement:
    if not isinstance(data, dict):
        data = {}
    return StructuralElement(
        id=_int_value(data.get("id"), 0),
        element_type=str(data.get("element_type") or ""),
        label=str(data.get("label") or ""),
        points=_points_value(data.get("points")),
        width=_float_value(data.get("width"), 0.0),
        length=_float_value(data.get("length"), 0.0),
        height=_float_value(data.get("height"), 0.0),
        arc_radius=_float_value(data.get("arc_radius"), 0.0),
        top_elevation=_float_value(data.get("top_elevation"), 0.0),
        stud_spacing=_float_value(data.get("stud_spacing"), 303.0),
        stud_width=_float_value(data.get("stud_width"), 65.0),
        board_thickness=_float_value(data.get("board_thickness"), 12.5),
        board_layers=_int_value(data.get("board_layers"), 1),
        is_stepped=bool(data.get("is_stepped", False)),
        parent_slab_id=_int_value(data.get("parent_slab_id"), -1),
        overlap_width=_float_value(data.get("overlap_width"), 0.0),
    )
