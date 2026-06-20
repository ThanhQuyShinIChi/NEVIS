from __future__ import annotations

from typing import Dict, Optional


def compute_edge_slope(
    start_z: float | None,
    end_z: float | None,
    length_2d: float | None,
) -> float | None:
    if start_z is None or end_z is None or length_2d is None:
        return None
    length = float(length_2d)
    if length <= 0.0:
        return None
    return (float(end_z) - float(start_z)) / length


def _format_number(value: float) -> str:
    rounded = round(float(value))
    if abs(float(value) - rounded) < 1e-9:
        return str(rounded)
    return f"{float(value):.6g}"


def format_z_label(
    z: Optional[float],
    prefix: str = "z=",
    unit: str = "mm",
) -> str:
    if z is None:
        return ""
    return f"{prefix}{_format_number(z)}{unit}"


def format_slope_label(
    start_z: Optional[float],
    end_z: Optional[float],
    length_2d: Optional[float],
    mode: str = "ratio",
) -> str:
    slope = compute_edge_slope(start_z, end_z, length_2d)
    if slope is None:
        return ""
    if mode == "percent":
        return f"{slope * 100.0:.2f}%"
    if mode == "decimal":
        return f"{slope:.4f}"

    if abs(slope) <= 1e-5:
        return "flat"
    return f"1/{_format_number(1.0 / abs(slope))}"


def edge_elevation_labels(
    start_z: Optional[float],
    end_z: Optional[float],
    length_2d: Optional[float],
    mode: str = "ratio",
) -> Dict[str, str]:
    return {
        "start_z": format_z_label(start_z),
        "end_z": format_z_label(end_z),
        "slope": format_slope_label(start_z, end_z, length_2d, mode=mode),
    }
