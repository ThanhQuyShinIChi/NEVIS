from __future__ import annotations

import copy
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem

import Nevis_no_ui as nevis


class QuickCheckHost:
    def __init__(self):
        self.model = nevis.PipeModel(
            nodes={
                1: nevis.Node(1, 0.0, 0.0),
                2: nevis.Node(2, 100.0, 0.0),
                3: nevis.Node(3, 200.0, 0.0),
            },
            edges=[
                nevis.Edge(1, 2, size="75", material_override="DV"),
                nevis.Edge(2, 3, size="50", material_override="DV"),
            ],
            fittings={2: nevis.Fitting(2, "Y", "75x50")},
        )
        self.library_index = [{"path": "available"}]
        self.table_mat = QTableWidget(0, 6)

    def edge_material(self, edge):
        return edge.material_override

    def library_pipe_sizes_for_material(self, material):
        return ["50"] if material == "DV" else []

    def matching_library_path(self, node_id, fitting_type, size):
        return "" if (node_id, fitting_type, size) == (2, "Y", "75x50") else "available"

    def build_material_rows(self, _sheet_type=""):
        return [["DV", "50", "DVパイプ", "m", 0.1, ""]]


class PipeQuickCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_reports_supported_library_fitting_and_bom_issues_without_mutation(self):
        host = QuickCheckHost()
        before = copy.deepcopy(host.model)

        issues = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(host.model, before)
        self.assertEqual(
            [(issue["check"], issue["target_kind"], issue["target_id"]) for issue in issues],
            [
                ("library", "edge", "1-2"),
                ("fitting", "node", 2),
                ("bom", "bom", ""),
            ],
        )

    def test_matching_visible_bom_does_not_create_warning(self):
        host = QuickCheckHost()
        host.model.edges = [nevis.Edge(1, 2, size="50", material_override="DV")]
        host.model.fittings = {}
        host.table_mat.setRowCount(1)
        for col, value in enumerate(["DV", "50", "DVパイプ", "m", "0.1", ""]):
            host.table_mat.setItem(0, col, QTableWidgetItem(value))

        issues = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(issues, [])

    def test_slope_format_is_checked_only_when_source_text_exists(self):
        host = QuickCheckHost()
        host.library_index = []
        host.model.edges = [nevis.Edge(1, 2, size="50")]
        host.model.fittings = {}
        host.build_material_rows = lambda _sheet_type="": []

        supported_issues = nevis.build_pipe_quick_check_issues(host)
        host.model.edges[0].slope_ratio_text = "2/100"
        invalid_issues = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(supported_issues, [])
        self.assertEqual(len(invalid_issues), 1)
        self.assertEqual(invalid_issues[0]["check"], "slope")

    def test_main_window_panel_is_read_only_and_retranslates(self):
        window = nevis.MainWindow()
        try:
            before = copy.deepcopy(window.model)
            window.open_pipe_check_panel()

            self.assertEqual(window.model, before)
            self.assertEqual(window.tabs.currentIndex(), window._pipe_check_tab_index)
            self.assertEqual(window.table_pipe_check.editTriggers(), QTableWidget.NoEditTriggers)
            self.assertEqual(window.btn_pipe_check.text(), "配管チェック")
            self.assertFalse(any("Apply" in button.text() for button in window.pipe_check_tab.findChildren(nevis.QPushButton)))

            window.lang = "vi"
            window.retranslate_pipe_check_ui()
            self.assertEqual(window.btn_pipe_check.text(), "Kiểm tra ống")
            self.assertEqual(window.table_pipe_check.horizontalHeaderItem(0).text(), "Mức độ")
        finally:
            window.close()

    def test_selecting_issue_highlights_without_changing_selection_and_close_clears(self):
        window = nevis.MainWindow()
        try:
            window.model = nevis.PipeModel(
                nodes={1: nevis.Node(1, 0.0, 0.0), 2: nevis.Node(2, 100.0, 0.0)},
                edges=[nevis.Edge(1, 2, size="50")],
            )
            window.selected_edge = "kept-selection"
            window._pipe_check_issues = [
                nevis._nevis_pipe_check_issue(
                    "error", "library", "edge", "1-2", "pipe_check_missing_size"
                )
            ]
            nevis._nevis_pipe_check_render(window)

            window.table_pipe_check.selectRow(0)
            QApplication.processEvents()

            self.assertEqual(window.selected_edge, "kept-selection")
            self.assertEqual(window._v82_quick_highlight, ("edge", "1-2"))

            window.close_pipe_check_panel()
            self.assertIsNone(window._v82_quick_highlight)
        finally:
            window.close()


if __name__ == "__main__":
    unittest.main()
