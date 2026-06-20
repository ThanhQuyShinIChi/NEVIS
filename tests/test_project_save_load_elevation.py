from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("NEVIS_SKIP_LICENSE", "1")

from PySide6.QtWidgets import QApplication

import Nevis_no_ui as nevis


class ProjectSaveLoadElevationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.window = nevis.MainWindow()

    def tearDown(self):
        self.window.close()
        self.temp_dir.cleanup()

    def _open_project(self, path: Path) -> None:
        with patch.object(nevis.QFileDialog, "getOpenFileName", return_value=(str(path), "JSON")):
            self.window.open_project()

    def test_elevation_values_round_trip_through_real_save_and_load(self):
        self.window.model = nevis.PipeModel(
            nodes={
                1: nevis.Node(1, 0.0, 0.0, 1500.0),
                2: nevis.Node(2, 15000.0, 0.0, 1200.0),
            },
            edges=[nevis.Edge(1, 2, "65", "", 0.02, start_z=1500.0, end_z=1200.0)],
        )
        path = Path(self.temp_dir.name) / "elevation.nevis.json"

        with patch.object(nevis.QFileDialog, "getSaveFileName", return_value=(str(path), "JSON")):
            self.window.save_project()

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["nodes"]["1"]["z"], 1500.0)
        self.assertEqual(payload["nodes"]["2"]["z"], 1200.0)
        self.assertEqual(payload["edges"][0]["start_z"], 1500.0)
        self.assertEqual(payload["edges"][0]["end_z"], 1200.0)
        self.assertEqual(payload["edges"][0]["slope"], 0.02)

        self.window.model = nevis.PipeModel()
        self._open_project(path)

        self.assertEqual(self.window.model.nodes[1].z, 1500.0)
        self.assertEqual(self.window.model.nodes[2].z, 1200.0)
        self.assertEqual(self.window.model.edges[0].start_z, 1500.0)
        self.assertEqual(self.window.model.edges[0].end_z, 1200.0)
        self.assertEqual(self.window.model.edges[0].slope, 0.02)

    def test_legacy_project_without_elevation_fields_loads_safe_defaults(self):
        path = Path(self.temp_dir.name) / "legacy.nevis.json"
        path.write_text(
            json.dumps({
                "nodes": {
                    "1": {"x": 0.0, "y": 0.0},
                    "2": {"x": 1000.0, "y": 0.0, "z": None},
                },
                "edges": [{"a": 1, "b": 2, "start_z": None, "end_z": "", "slope": None}],
            }),
            encoding="utf-8",
        )

        self._open_project(path)

        self.assertEqual(self.window.model.nodes[1].z, 0.0)
        self.assertEqual(self.window.model.nodes[2].z, 0.0)
        edge = self.window.model.edges[0]
        self.assertIsNone(edge.start_z)
        self.assertIsNone(edge.end_z)
        self.assertEqual(edge.slope, 0.0)


if __name__ == "__main__":
    unittest.main()
