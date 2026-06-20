# NEVIS — Chuyển bản vẽ PDF/Ảnh → DXF

Tool chuyển bản vẽ xây dựng (PDF hoặc ảnh) sang **DXF** để CAD đọc được.
Viết bằng PySide6 để sau ghép thẳng vào NEVIS.

## Hai nhánh

| Nhánh | Đầu vào | Cách làm | Chất lượng |
|-------|---------|----------|-----------|
| **Vector** | PDF xuất từ CAD (còn line/arc) | Đọc hình học trực tiếp (PyMuPDF) → DXF | Cao, gần như chính xác |
| **Raster** | Ảnh / PDF scan / ảnh chụp | OpenCV (nhị phân + Hough) + OCR (tùy chọn) → DXF | Gần đúng, **cần dọn tay trong CAD** |

Tự động phát hiện vector/raster, hoặc ép chế độ.

## Chạy

```bash
# Form UI
python -m tools.cad_converter.app

# CLI
python -m tools.cad_converter.converter input.pdf output.dxf
python -m tools.cad_converter.converter scan.png --mode raster --dpi 300 --ocr
```

## Dùng như thư viện (để tích hợp NEVIS)

```python
from tools.cad_converter import convert, ConvertOptions
res = convert("ban_ve.pdf", "ban_ve.dxf", ConvertOptions(raster_dpi=300))
print(res.summary())
```

## Phụ thuộc

- Bắt buộc: `PyMuPDF`, `ezdxf`, `numpy`
- Nhánh raster: `opencv-python-headless`
- OCR (tùy chọn): binary **Tesseract-OCR** + `pytesseract`. Thiếu vẫn convert hình học bình thường.

```bash
pip install PyMuPDF ezdxf numpy opencv-python-headless pytesseract
```

Tesseract binary (Windows): tải UB-Mannheim build, rồi nếu không nằm trong PATH:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## Layer DXF xuất ra

- `NEVIS_GEOMETRY` — line/curve/rect từ PDF vector
- `NEVIS_RASTER_LINES` — đoạn thẳng dò từ ảnh
- `NEVIS_TEXT` — text (vector) hoặc OCR

## Còn thiếu / hướng tiếp (Phase sau)

- Xuất thẳng **JWW/JWC** (tái dùng exporter sẵn có của NEVIS) thay vì chỉ DXF
- Raster đa trang (hiện chỉ trang đầu)
- Gộp/duỗi đoạn Hough collinear để bản vẽ sạch hơn
- Nhận diện ký hiệu MEP (van, fitting) bằng model object-detection
- Ánh xạ nét → mô hình ống của NEVIS (không chỉ là geometry chết)
