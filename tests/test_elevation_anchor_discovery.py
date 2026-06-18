from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from modules.elevation_anchor import discover_elevation_anchors


@dataclass
class DummyNode:
    id: int
    x: float = 0.0
    y: float = 0.0
    z: Optional[float] = None
    level_id: str = ""


@dataclass
class DummyEdge:
    a: int
    b: int
    start_level_id: Optional[str] = None
    end_level_id: Optional[str] = None
    start_z: Optional[float] = None
    end_z: Optional[float] = None

    @property
    def key(self) -> str:
        return f"{min(self.a, self.b)}-{max(self.a, self.b)}"


@dataclass
class DummyLevelDatum:
    id: str
    elevation_mm: float


@dataclass
class DummyPipeModel:
    nodes: Dict[int, DummyNode] = field(default_factory=dict)
    edges: List[DummyEdge] = field(default_factory=list)
    level_datums: Dict[str, DummyLevelDatum] = field(default_factory=dict)


class ElevationAnchorDiscoveryTest(unittest.TestCase):
    def test_edge_explicit_start_end_z_become_known_endpoints(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2)},
            edges=[DummyEdge(1, 2, start_z=0.0, end_z=-30.0)],
        )

        result = discover_elevation_anchors(model)

        self.assertEqual(result.known_endpoint_z[(0, "start")], 0.0)
        self.assertEqual(result.known_endpoint_z[(0, "end")], -30.0)
        self.assertEqual(len(result.endpoint_anchors), 2)
        self.assertEqual(len(result.initial_frontier), 2)

    def test_edge_level_ids_resolve_to_level_datum_elevation(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2)},
            edges=[DummyEdge(1, 2, start_level_id="1F_FL", end_level_id="B1_FL")],
            level_datums={
                "1F_FL": DummyLevelDatum("1F_FL", 0.0),
                "B1_FL": DummyLevelDatum("B1_FL", -3000.0),
            },
        )

        result = discover_elevation_anchors(model)

        self.assertEqual(result.known_endpoint_z[(0, "start")], 0.0)
        self.assertEqual(result.known_endpoint_z[(0, "end")], -3000.0)
        self.assertEqual(result.endpoint_anchors[(0, "start")].source, "edge.start_level_id")
        self.assertEqual(result.endpoint_anchors[(0, "end")].source, "edge.end_level_id")

    def test_node_level_id_becomes_node_anchor_without_using_node_z(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1, z=9999.0, level_id="1F_FL")},
            level_datums={"1F_FL": DummyLevelDatum("1F_FL", 0.0)},
        )

        result = discover_elevation_anchors(model)

        self.assertEqual(result.node_anchors[1].z, 0.0)
        self.assertEqual(result.node_anchors[1].source, "node.level_id")
        self.assertEqual(len(result.initial_frontier), 1)

    def test_empty_elevation_model_has_no_known_or_frontier(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1), 2: DummyNode(2)},
            edges=[DummyEdge(1, 2)],
        )

        result = discover_elevation_anchors(model)

        self.assertEqual(result.known_endpoint_z, {})
        self.assertEqual(result.node_anchors, {})
        self.assertEqual(result.initial_frontier, [])

    def test_discovery_does_not_mutate_model(self):
        model = DummyPipeModel(
            nodes={1: DummyNode(1, z=123.0, level_id="1F_FL"), 2: DummyNode(2)},
            edges=[DummyEdge(1, 2, start_z=0.0, end_level_id="1F_FL")],
            level_datums={"1F_FL": DummyLevelDatum("1F_FL", 0.0)},
        )
        before = copy.deepcopy(model)

        discover_elevation_anchors(model)

        self.assertEqual(model, before)


if __name__ == "__main__":
    unittest.main()
