"""
Form PySide6 cho bộ chuyển PDF/ảnh -> DXF.

Chạy độc lập:   python -m tools.cad_converter.app
Khi tích hợp NEVIS: import ConverterDialog rồi .exec() từ menu/nút.

Convert chạy trong QThread để UI không bị treo.
"""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton,
    QPlainTextEdit, QSpinBox, QVBoxLayout, QWidget,
)

from . import converter as C


class _Worker(QObject):
    progress = Signal(float, str)
    done = Signal(object)        # ConvertResult
    failed = Signal(str)

    def __init__(self, src: str, out: str, opts: C.ConvertOptions):
        super().__init__()
        self._src, self._out, self._opts = src, out, opts

    def run(self):
        try:
            res = C.convert(
                self._src, self._out, self._opts,
                progress=lambda p, m: self.progress.emit(p, m),
            )
            self.done.emit(res)
        except Exception as e:  # noqa: BLE001
            self.failed.emit(f"{type(e).__name__}: {e}")


class ConverterDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("NEVIS — Chuyển bản vẽ (PDF/Ảnh) → DXF")
        self.setMinimumWidth(560)
        self._thread: QThread | None = None
        self._build_ui()
        self._refresh_env_hint()

    # ----------------------------------------------------------------- UI --
    def _build_ui(self):
        root = QVBoxLayout(self)

        # --- file vào / ra ---
        files = QGroupBox("File")
        f = QFormLayout(files)
        self.in_edit = QLineEdit()
        in_btn = QPushButton("Chọn…")
        in_btn.clicked.connect(self._pick_input)
        in_row = QHBoxLayout()
        in_row.addWidget(self.in_edit)
        in_row.addWidget(in_btn)
        f.addRow("Đầu vào:", _wrap(in_row))

        self.out_edit = QLineEdit()
        out_btn = QPushButton("Chọn…")
        out_btn.clicked.connect(self._pick_output)
        out_row = QHBoxLayout()
        out_row.addWidget(self.out_edit)
        out_row.addWidget(out_btn)
        f.addRow("DXF ra:", _wrap(out_row))
        root.addWidget(files)

        # --- chế độ ---
        mode_box = QGroupBox("Chế độ")
        mf = QFormLayout(mode_box)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Tự động", "Vector (PDF từ CAD)", "Raster (ảnh/scan)"])
        self.mode_combo.currentIndexChanged.connect(self._sync_raster_enabled)
        mf.addRow("Loại bản vẽ:", self.mode_combo)
        self.text_chk = QCheckBox("Trích xuất text (vector)")
        self.text_chk.setChecked(True)
        mf.addRow("", self.text_chk)
        root.addWidget(mode_box)

        # --- tham số raster ---
        self.raster_box = QGroupBox("Tham số ảnh / scan")
        rf = QFormLayout(self.raster_box)
        self.dpi_spin = _spin(72, 1200, 300, 50)
        rf.addRow("DPI rasterize PDF:", self.dpi_spin)
        self.hough_thr = _spin(10, 500, 80, 5)
        rf.addRow("Hough threshold:", self.hough_thr)
        self.hough_min = _spin(5, 1000, 40, 5)
        rf.addRow("Độ dài đoạn tối thiểu (px):", self.hough_min)
        self.hough_gap = _spin(0, 100, 8, 1)
        rf.addRow("Khoảng hở nối (px):", self.hough_gap)
        self.invert_chk = QCheckBox("Đảo nền (nét trắng / nền đen)")
        rf.addRow("", self.invert_chk)
        self.ocr_chk = QCheckBox("Bật OCR text (cần Tesseract)")
        rf.addRow("", self.ocr_chk)
        root.addWidget(self.raster_box)

        # --- môi trường ---
        self.env_lbl = QLabel()
        self.env_lbl.setWordWrap(True)
        self.env_lbl.setStyleSheet("color:#a06000;")
        root.addWidget(self.env_lbl)

        # --- tiến trình + log ---
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        root.addWidget(self.bar)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        root.addWidget(self.log)

        # --- nút ---
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.convert_btn = QPushButton("Chuyển đổi")
        self.convert_btn.setDefault(True)
        self.convert_btn.clicked.connect(self._start)
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.convert_btn)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

        self._sync_raster_enabled()

    # -------------------------------------------------------------- helpers --
    def _refresh_env_hint(self):
        msgs = []
        if not C.opencv_available():
            msgs.append("⚠ Thiếu OpenCV → không xử lý được ảnh/scan (pip install opencv-python-headless).")
        if not C.tesseract_available():
            msgs.append("ℹ OCR tắt: chưa có Tesseract binary. Hình học vẫn convert bình thường.")
            self.ocr_chk.setEnabled(False)
            self.ocr_chk.setChecked(False)
        self.env_lbl.setText("\n".join(msgs))
        self.env_lbl.setVisible(bool(msgs))

    def _sync_raster_enabled(self):
        # bật ô tham số raster khi mode = Tự động hoặc Raster
        is_vector_only = self.mode_combo.currentIndex() == 1
        self.raster_box.setEnabled(not is_vector_only)

    def _pick_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn bản vẽ", "",
            "Bản vẽ (*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp);;Tất cả (*.*)",
        )
        if path:
            self.in_edit.setText(path)
            if not self.out_edit.text().strip():
                self.out_edit.setText(os.path.splitext(path)[0] + ".dxf")

    def _pick_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu DXF", self.out_edit.text() or "", "DXF (*.dxf)"
        )
        if path:
            self.out_edit.setText(path)

    def _opts(self) -> C.ConvertOptions:
        idx = self.mode_combo.currentIndex()
        force = {0: None, 1: "vector", 2: "raster"}[idx]
        return C.ConvertOptions(
            force_mode=force,
            extract_text=self.text_chk.isChecked(),
            raster_dpi=self.dpi_spin.value(),
            hough_threshold=self.hough_thr.value(),
            hough_min_line=self.hough_min.value(),
            hough_max_gap=self.hough_gap.value(),
            invert_binary=self.invert_chk.isChecked(),
            enable_ocr=self.ocr_chk.isChecked(),
        )

    def _log(self, msg: str):
        self.log.appendPlainText(msg)

    # --------------------------------------------------------------- chạy --
    def _start(self):
        src = self.in_edit.text().strip()
        out = self.out_edit.text().strip()
        if not src or not os.path.isfile(src):
            self._log("✗ Chưa chọn file đầu vào hợp lệ.")
            return
        if not out:
            out = os.path.splitext(src)[0] + ".dxf"
            self.out_edit.setText(out)

        self.convert_btn.setEnabled(False)
        self.bar.setValue(0)
        self.log.clear()
        self._log(f"Bắt đầu: {os.path.basename(src)}")

        self._thread = QThread(self)
        self._worker = _Worker(src, out, self._opts())
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.done.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)
        self._thread.start()

    def _on_progress(self, pct: float, msg: str):
        self.bar.setValue(int(pct * 100))
        self._log(f"[{pct:5.0%}] {msg}")

    def _on_done(self, res: C.ConvertResult):
        self._log("\n✓ XONG\n" + res.summary())
        self._log(f"\n→ {res.output_path}")
        self._finish()

    def _on_failed(self, err: str):
        self._log("\n✗ LỖI: " + err)
        self._finish()

    def _finish(self):
        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
        self.convert_btn.setEnabled(True)


# ------------------------------------------------------------------ utils --
def _wrap(layout) -> QWidget:
    w = QWidget()
    layout.setContentsMargins(0, 0, 0, 0)
    w.setLayout(layout)
    return w


def _spin(lo: int, hi: int, val: int, step: int) -> QSpinBox:
    s = QSpinBox()
    s.setRange(lo, hi)
    s.setValue(val)
    s.setSingleStep(step)
    return s


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    dlg = ConverterDialog()
    dlg.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
