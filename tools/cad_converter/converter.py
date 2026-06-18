"""
NEVIS - Bộ chuyển bản vẽ (PDF / ảnh) sang DXF.

Hai nhánh xử lý:

  1. Vector  : PDF còn hình học bên trong (xuất từ CAD).
               -> Đọc trực tiếp line/curve/rect + text bằng PyMuPDF,
                  ghi thẳng ra DXF. Chất lượng cao, deterministic.

  2. Raster  : ảnh / PDF scan / ảnh chụp (chỉ là pixel).
               -> Tiền xử lý OpenCV + Hough line + OCR (tùy chọn),
                  vector hóa gần đúng. Kết quả cần dọn tay.

Tọa độ: PDF/ảnh gốc ở góc trên-trái, y hướng xuống.
DXF dùng y hướng lên, nên mọi y đều bị lật: dxf_y = height - src_y.

Phụ thuộc: PyMuPDF (fitz), ezdxf, opencv-python(-headless), numpy.
OCR cần thêm binary Tesseract-OCR + pytesseract (tùy chọn).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional

import ezdxf
import fitz  # PyMuPDF
import numpy as np

try:  # OpenCV chỉ cần cho nhánh raster
    import cv2

    _HAS_CV2 = True
except Exception:  # pragma: no cover
    _HAS_CV2 = False

try:  # OCR là tùy chọn, thiếu binary Tesseract vẫn chạy được
    import pytesseract

    _HAS_TESS_MODULE = True
except Exception:  # pragma: no cover
    _HAS_TESS_MODULE = False


# Layer đích trong file DXF
LAYER_GEOMETRY = "NEVIS_GEOMETRY"
LAYER_TEXT = "NEVIS_TEXT"
LAYER_RASTER = "NEVIS_RASTER_LINES"

RASTER_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


# --------------------------------------------------------------------------- #
# Cấu hình & kết quả
# --------------------------------------------------------------------------- #
@dataclass
class ConvertOptions:
    """Tham số điều khiển quá trình convert."""

    # chung
    force_mode: Optional[str] = None  # None=auto, "vector", "raster"
    extract_text: bool = True

    # nhánh raster
    raster_dpi: int = 300            # độ phân giải rasterize PDF scan
    hough_threshold: int = 80        # ngưỡng tích lũy Hough
    hough_min_line: int = 40         # độ dài đoạn tối thiểu (px)
    hough_max_gap: int = 8           # khoảng hở tối đa để nối (px)
    invert_binary: bool = False      # nét trắng / nền đen thì bật
    enable_ocr: bool = False         # cần Tesseract binary

    # đơn vị: pixel -> đơn vị bản vẽ (vd 1.0 = giữ nguyên px)
    raster_scale: float = 1.0


@dataclass
class ConvertResult:
    output_path: str
    mode: str
    page_count: int = 0
    line_count: int = 0
    curve_count: int = 0
    text_count: int = 0
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [
            f"Mode: {self.mode}",
            f"Trang: {self.page_count}",
            f"Đường: {self.line_count}",
            f"Cung/curve: {self.curve_count}",
            f"Text: {self.text_count}",
        ]
        s = " | ".join(parts)
        if self.warnings:
            s += "\nCảnh báo:\n  - " + "\n  - ".join(self.warnings)
        return s


ProgressFn = Callable[[float, str], None]


def _noop(_pct: float, _msg: str) -> None:
    pass


# --------------------------------------------------------------------------- #
# Tiện ích kiểm tra môi trường (UI dùng để cảnh báo người dùng)
# --------------------------------------------------------------------------- #
def tesseract_available() -> bool:
    if not _HAS_TESS_MODULE:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def opencv_available() -> bool:
    return _HAS_CV2


# --------------------------------------------------------------------------- #
# Auto-detect: file là vector hay raster
# --------------------------------------------------------------------------- #
def detect_mode(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in RASTER_EXTS:
        return "raster"
    if ext == ".pdf":
        try:
            doc = fitz.open(path)
            try:
                # Đếm số "path item" thực sự (line/curve/rect) trên vài trang đầu.
                # PDF scan thường chỉ là 1 ảnh nhúng -> ~0 path; PDF từ CAD -> rất nhiều.
                vector_items = 0
                for page in doc[: min(3, doc.page_count)]:
                    for d in page.get_drawings():
                        vector_items += len(d.get("items", ()))
                return "vector" if vector_items >= 3 else "raster"
            finally:
                doc.close()
        except Exception:
            return "raster"
    # mặc định coi như raster (an toàn hơn)
    return "raster"


# --------------------------------------------------------------------------- #
# Nhánh VECTOR: PyMuPDF -> DXF
# --------------------------------------------------------------------------- #
def _convert_vector(path: str, out_path: str, opts: ConvertOptions,
                    progress: ProgressFn) -> ConvertResult:
    doc = fitz.open(path)
    dxf = ezdxf.new(dxfversion="R2010")
    msp = dxf.modelspace()
    for name in (LAYER_GEOMETRY, LAYER_TEXT):
        if name not in dxf.layers:
            dxf.layers.add(name)

    res = ConvertResult(output_path=out_path, mode="vector",
                        page_count=doc.page_count)

    # Mỗi trang được dịch sang phải để không chồng lên nhau (multi-page)
    x_offset = 0.0
    page_gap = 50.0

    for pi, page in enumerate(doc):
        h = page.rect.height
        w = page.rect.width

        def fy(y: float) -> float:  # lật trục y
            return h - y

        # ---- hình học ----
        for d in page.get_drawings():
            for item in d["items"]:
                kind = item[0]
                if kind == "l":  # line: p1, p2
                    p1, p2 = item[1], item[2]
                    msp.add_line(
                        (p1.x + x_offset, fy(p1.y)),
                        (p2.x + x_offset, fy(p2.y)),
                        dxfattribs={"layer": LAYER_GEOMETRY},
                    )
                    res.line_count += 1
                elif kind == "re":  # rectangle
                    r = item[1]
                    pts = [
                        (r.x0 + x_offset, fy(r.y0)),
                        (r.x1 + x_offset, fy(r.y0)),
                        (r.x1 + x_offset, fy(r.y1)),
                        (r.x0 + x_offset, fy(r.y1)),
                    ]
                    msp.add_lwpolyline(pts, close=True,
                                       dxfattribs={"layer": LAYER_GEOMETRY})
                    res.line_count += 4
                elif kind == "c":  # bezier cubic: p1,p2,p3,p4
                    p1, p2, p3, p4 = item[1], item[2], item[3], item[4]
                    pts = _flatten_cubic(
                        (p1.x, p1.y), (p2.x, p2.y),
                        (p3.x, p3.y), (p4.x, p4.y), steps=16,
                    )
                    pts = [(x + x_offset, fy(y)) for (x, y) in pts]
                    msp.add_lwpolyline(pts, dxfattribs={"layer": LAYER_GEOMETRY})
                    res.curve_count += 1
                elif kind == "qu":  # quad
                    q = item[1]
                    pts = [
                        (q.ul.x + x_offset, fy(q.ul.y)),
                        (q.ur.x + x_offset, fy(q.ur.y)),
                        (q.lr.x + x_offset, fy(q.lr.y)),
                        (q.ll.x + x_offset, fy(q.ll.y)),
                    ]
                    msp.add_lwpolyline(pts, close=True,
                                       dxfattribs={"layer": LAYER_GEOMETRY})
                    res.line_count += 4

        # ---- text ----
        if opts.extract_text:
            td = page.get_text("dict")
            for block in td.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        txt = span.get("text", "").strip()
                        if not txt:
                            continue
                        ox, oy = span["origin"]
                        size = max(span.get("size", 8.0), 1.0)
                        msp.add_text(
                            txt,
                            dxfattribs={
                                "layer": LAYER_TEXT,
                                "height": size,
                            },
                        ).set_placement((ox + x_offset, fy(oy)))
                        res.text_count += 1

        x_offset += w + page_gap
        progress((pi + 1) / max(doc.page_count, 1) * 0.95,
                 f"Trang {pi + 1}/{doc.page_count}")

    doc.close()
    dxf.saveas(out_path)
    progress(1.0, "Hoàn tất (vector)")
    return res


def _flatten_cubic(p0, p1, p2, p3, steps: int = 16):
    """Băm bezier bậc 3 thành polyline."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = (mt**3 * p0[0] + 3 * mt**2 * t * p1[0]
             + 3 * mt * t**2 * p2[0] + t**3 * p3[0])
        y = (mt**3 * p0[1] + 3 * mt**2 * t * p1[1]
             + 3 * mt * t**2 * p2[1] + t**3 * p3[1])
        pts.append((x, y))
    return pts


# --------------------------------------------------------------------------- #
# Nhánh RASTER: OpenCV -> DXF
# --------------------------------------------------------------------------- #
def _load_raster(path: str, dpi: int) -> np.ndarray:
    """Trả về ảnh BGR. PDF scan được rasterize ở dpi cho trước."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        doc = fitz.open(path)
        page = doc[0]  # prototype: trang đầu
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        doc.close()
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return img
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Không đọc được ảnh: {path}")
    return img


def _convert_raster(path: str, out_path: str, opts: ConvertOptions,
                    progress: ProgressFn) -> ConvertResult:
    if not _HAS_CV2:
        raise RuntimeError("Cần opencv-python để xử lý ảnh/scan.")

    progress(0.05, "Nạp ảnh…")
    img = _load_raster(path, opts.raster_dpi)
    h = img.shape[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    progress(0.2, "Nhị phân hóa…")
    # Adaptive threshold để chịu được nền không đều / scan mờ
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 31, 10,
    )
    if opts.invert_binary:
        binary = cv2.bitwise_not(binary)

    progress(0.45, "Dò đường (Hough)…")
    lines = cv2.HoughLinesP(
        binary, 1, np.pi / 180,
        threshold=opts.hough_threshold,
        minLineLength=opts.hough_min_line,
        maxLineGap=opts.hough_max_gap,
    )

    dxf = ezdxf.new(dxfversion="R2010")
    msp = dxf.modelspace()
    for name in (LAYER_RASTER, LAYER_TEXT):
        if name not in dxf.layers:
            dxf.layers.add(name)

    res = ConvertResult(output_path=out_path, mode="raster", page_count=1)
    s = opts.raster_scale

    if lines is not None:
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            msp.add_line(
                (x1 * s, (h - y1) * s),
                (x2 * s, (h - y2) * s),
                dxfattribs={"layer": LAYER_RASTER},
            )
            res.line_count += 1
    else:
        res.warnings.append(
            "Không dò được đường nào — thử giảm Hough threshold / "
            "min line, hoặc bật 'đảo nền'."
        )

    # ---- OCR (tùy chọn) ----
    if opts.enable_ocr:
        progress(0.75, "OCR text…")
        if not tesseract_available():
            res.warnings.append(
                "Bật OCR nhưng không tìm thấy Tesseract binary — bỏ qua text. "
                "Cài Tesseract-OCR rồi đặt đường dẫn để dùng."
            )
        else:
            try:
                data = pytesseract.image_to_data(
                    gray, output_type=pytesseract.Output.DICT
                )
                n = len(data["text"])
                for i in range(n):
                    txt = (data["text"][i] or "").strip()
                    conf = float(data["conf"][i]) if data["conf"][i] != "-1" else -1
                    if not txt or conf < 40:
                        continue
                    tx = data["left"][i]
                    ty = data["top"][i]
                    th = max(data["height"][i], 6)
                    msp.add_text(
                        txt,
                        dxfattribs={"layer": LAYER_TEXT, "height": th * s},
                    ).set_placement((tx * s, (h - ty - th) * s))
                    res.text_count += 1
            except Exception as e:  # pragma: no cover
                res.warnings.append(f"OCR lỗi: {e}")

    progress(0.95, "Ghi DXF…")
    dxf.saveas(out_path)
    res.warnings.append(
        "Bản vẽ raster được vector hóa gần đúng — cần kiểm tra & dọn lại trong CAD."
    )
    progress(1.0, "Hoàn tất (raster)")
    return res


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def convert(path: str, out_path: str,
            opts: Optional[ConvertOptions] = None,
            progress: Optional[ProgressFn] = None) -> ConvertResult:
    """Convert một file (PDF/ảnh) sang DXF."""
    opts = opts or ConvertOptions()
    progress = progress or _noop

    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    mode = opts.force_mode or detect_mode(path)
    progress(0.0, f"Bắt đầu ({mode})…")

    if mode == "vector":
        return _convert_vector(path, out_path, opts, progress)
    return _convert_raster(path, out_path, opts, progress)


if __name__ == "__main__":
    import argparse
    import sys

    # Console Windows hay là cp932/cp1258 -> ép utf-8 để in được tiếng Việt
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="NEVIS PDF/ảnh -> DXF")
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--mode", choices=["vector", "raster"], default=None)
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--ocr", action="store_true")
    ap.add_argument("--no-text", action="store_true")
    a = ap.parse_args()

    out = a.output or (os.path.splitext(a.input)[0] + ".dxf")
    o = ConvertOptions(
        force_mode=a.mode, raster_dpi=a.dpi,
        enable_ocr=a.ocr, extract_text=not a.no_text,
    )
    r = convert(a.input, out, o, progress=lambda p, m: print(f"[{p:5.0%}] {m}"))
    print("\n" + r.summary())
    print("→", r.output_path)
