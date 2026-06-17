from __future__ import annotations
from dataclasses import dataclass
from .graph import PipeGraph

@dataclass
class MaterialItem:
    name: str
    qty: float
    unit: str


def rough_materials(graph: PipeGraph, pipe_type: str = "TMP", main_size: str = "65") -> list[MaterialItem]:
    total_len = sum(e.length for e in graph.edges.values()) / 1000.0  # assume JWW mm -> m
    return [
        MaterialItem(f"Ống {pipe_type}{main_size}", round(total_len, 2), "m"),
        MaterialItem("Điểm cuối nhánh", len(graph.endpoints), "điểm"),
        MaterialItem("Điểm giao nhánh", len(graph.junctions), "điểm"),
        MaterialItem("Đoạn tim ống", len(graph.edges), "đoạn"),
    ]
