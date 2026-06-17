from __future__ import annotations

from dataclasses import dataclass, field
import math
from collections import defaultdict, deque
from .parser import Segment

@dataclass
class Node:
    id: int
    x: float
    y: float
    edges: set[int] = field(default_factory=set)

@dataclass
class Edge:
    id: int
    a: int
    b: int
    length: float
    segment: Segment

@dataclass
class PipeGraph:
    nodes: dict[int, Node]
    edges: dict[int, Edge]
    endpoints: list[int]
    junctions: list[int]

    def nearest_node(self, x: float, y: float) -> int | None:
        if not self.nodes:
            return None
        return min(self.nodes, key=lambda nid: math.hypot(self.nodes[nid].x - x, self.nodes[nid].y - y))

    def distances_from(self, root: int) -> dict[int, float]:
        dist = {root: 0.0}
        q = deque([root])
        while q:
            n = q.popleft()
            for eid in self.nodes[n].edges:
                e = self.edges[eid]
                m = e.b if e.a == n else e.a
                nd = dist[n] + e.length
                if m not in dist or nd < dist[m]:
                    dist[m] = nd
                    q.append(m)
        return dist


def _key(x: float, y: float, tol: float) -> tuple[int, int]:
    return (round(x / tol), round(y / tol))


def build_graph(segments: list[Segment], tol: float = 0.01) -> PipeGraph:
    nodes: dict[int, Node] = {}
    key_to_id: dict[tuple[int, int], int] = {}
    edges: dict[int, Edge] = {}

    def get_node(x: float, y: float) -> int:
        k = _key(x, y, tol)
        if k in key_to_id:
            return key_to_id[k]
        nid = len(nodes) + 1
        key_to_id[k] = nid
        nodes[nid] = Node(nid, x, y)
        return nid

    for seg in segments:
        a = get_node(seg.x1, seg.y1)
        b = get_node(seg.x2, seg.y2)
        if a == b:
            continue
        eid = len(edges) + 1
        edges[eid] = Edge(eid, a, b, seg.length, seg)
        nodes[a].edges.add(eid)
        nodes[b].edges.add(eid)

    endpoints = sorted([nid for nid, n in nodes.items() if len(n.edges) == 1])
    junctions = sorted([nid for nid, n in nodes.items() if len(n.edges) >= 3])
    return PipeGraph(nodes=nodes, edges=edges, endpoints=endpoints, junctions=junctions)
