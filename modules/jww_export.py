from __future__ import annotations
from pathlib import Path
from .graph import PipeGraph


def export_debug_jww(graph: PipeGraph, out_path: str | Path = "jwc_out.txt") -> None:
    """Temporary export: return centerline + endpoint/junction markers to JWW.

    This is only for checking coordinate round-trip. Later this will draw pipe edges,
    fittings, text, layers, colors and material marks.
    """
    lines: list[str] = []
    lines += ["lg0", "lyb", "lc6", "lt5"]
    for e in graph.edges.values():
        s = e.segment
        lines.append(f"{s.x1:.10f} {s.y1:.10f} {s.x2:.10f} {s.y2:.10f}")

    # endpoints in red-like color lc2, junctions in lc3 for quick visual check.
    lines += ["lyc", "lc2", "lt1"]
    for nid in graph.endpoints:
        n = graph.nodes[nid]
        lines.append(f"ci {n.x:.10f} {n.y:.10f} 35.0000000000")

    lines += ["lc3", "lt1"]
    for nid in graph.junctions:
        n = graph.nodes[nid]
        lines.append(f"ci {n.x:.10f} {n.y:.10f} 50.0000000000")

    Path(out_path).write_text("\n".join(lines) + "\n", encoding="cp932", errors="ignore")
