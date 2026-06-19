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


class TmpFallbackHost(QuickCheckHost):
    def __init__(self, sizes):
        super().__init__()
        self.model.edges = [nevis.Edge(1, 2, size="30", material_override="TMP")]
        self.model.fittings = {2: nevis.Fitting(2, "Y", "30x30")}
        self._nevis_master_data = {"materials": [{"code": "TMP", "sizes": list(sizes)}]}

    def resolve_fitting_library_path_for_jww(self, node_id, fitting):
        # NEVIS intentionally permits this resolver to select an approved DV fallback.
        return "DV_Y_30_30.json"

    def build_material_rows(self, _sheet_type=""):
        return []


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
        self.assertEqual([issue["code"] for issue in issues], ["E102", "E202", ""])

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

    def test_tmp_size_and_approved_dv_fitting_fallback_do_not_report_false_errors(self):
        host = TmpFallbackHost(["30", "40"])

        issues = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(issues, [])

    def test_tmp_size_missing_from_material_db_has_short_specific_message(self):
        host = TmpFallbackHost(["40", "50"])

        issues = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["message"], "pipe_check_size_missing")
        self.assertEqual(issues[0]["message_args"], {"size": "30", "material": "TMP"})
        self.assertEqual(issues[0]["code"], "E102")

    def test_missing_pipe_size_has_e101(self):
        host = QuickCheckHost()
        host.model.edges = [nevis.Edge(1, 2, size="")]
        host.model.fittings = {}
        host.build_material_rows = lambda _sheet_type="": []

        issues = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["code"], "E101")

    def test_missing_fitting_library_has_e202(self):
        host = QuickCheckHost()
        host.model.edges = []
        host.build_material_rows = lambda _sheet_type="": []

        issues = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["code"], "E202")

    def test_incomplete_fitting_has_e201_and_missing_size_variant_has_e203(self):
        host = QuickCheckHost()
        host.model.edges = []
        host.build_material_rows = lambda _sheet_type="": []
        host.model.fittings = {2: nevis.Fitting(2, "", "")}

        incomplete = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(incomplete[0]["code"], "E201")

        host.model.fittings = {2: nevis.Fitting(2, "Y", "75x50")}
        host.current_pipe_for_node = lambda _node_id: "DV"
        host.library_sizes = lambda _pipe, _ftype: ["50x40", "65x50"]

        missing_size = nevis.build_pipe_quick_check_issues(host)

        self.assertEqual(missing_size[0]["code"], "E203")

    def test_main_window_panel_is_read_only_and_retranslates(self):
        window = nevis.MainWindow()
        try:
            before = copy.deepcopy(window.model)
            window.open_pipe_check_panel()

            self.assertEqual(window.model, before)
            self.assertEqual(window.tabs.currentIndex(), window._pipe_check_tab_index)
            self.assertEqual(window.table_pipe_check.editTriggers(), QTableWidget.NoEditTriggers)
            self.assertGreaterEqual(window.table_pipe_check.horizontalHeader().height(), 38)
            self.assertTrue(window.table_pipe_check.wordWrap())
            self.assertGreaterEqual(window.table_pipe_check.columnWidth(2), 125)
            self.assertEqual(window.btn_pipe_check.text(), "配管チェック")
            self.assertFalse(any("Apply" in button.text() for button in window.pipe_check_tab.findChildren(nevis.QPushButton)))

            window.lang = "vi"
            window.retranslate_pipe_check_ui()
            self.assertEqual(window.btn_pipe_check.text(), "Kiểm tra ống")
            self.assertEqual(window.table_pipe_check.horizontalHeaderItem(0).text(), "Mức độ")

            window._pipe_check_issues = [
                nevis._nevis_pipe_check_issue(
                    "error", "library", "edge", "1-2", "pipe_check_size_missing",
                    {"size": "30", "material": "TMP"}, code="E102"
                )
            ]
            nevis._nevis_pipe_check_render(window)
            self.assertEqual(window.table_pipe_check.item(0, 3).text(), "[E102] TMP: không có cỡ 30")
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
