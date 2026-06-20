# PIPE CODE — Vùng Khóa / 配管コード保護区域

> **CẢNH BÁO:** Các section liệt kê dưới đây đã được kiểm tra và chốt.
> Không sửa khi vá các tính năng khác (structural, section view, JWW export...).
> Nếu cần sửa, đọc toàn bộ file này trước, test lại pipe rendering sau khi sửa.

---

## 1. Tiêu chuẩn nét ống — `Nevis_no_ui.py` dòng ~210–252

**Biến liên quan:** `PIPE_COLORS`, `NEVIS_PIPE_STYLE_LOCKED_VERSION`,
`NEVIS_PREVIEW_CENTERLINE_STYLE`, `NEVIS_PREVIEW_CENTERLINE_DASH_PATTERN`

**Quy tắc đã chốt (LOCKED 2026-06):**
- **VP / DV / VU / HTVP / TaikaVP:** 5 nét (2 biên liền + 2 trong đứt + 1 tim gạch-chấm)
- **TMP / トミジ:** 7 nét (4 biên liền 2 bên + 2 trong đứt 2 bên + 1 tim)
- Tim ống dùng `CustomDashLine` pattern `[4, 3, 12, 3]` trong preview
- Tim ống xuất JWW dùng LT5 (一点鎖1)
- **Không vẽ nét ngang thừa** tại điểm giáp ranh chống cháy (`NEVIS_FIRE_BOUNDARY_NO_EXTRA_CAP_2026_06_12 = True`)

---

## 2. Pipe Rendering — `paintEvent` dòng ~2123

**Class:** `PreviewView` (hoặc class preview tương đương)

**Không được sửa:**
- Thứ tự vẽ các nét (biên → trong → tim) — đảo thứ tự sẽ làm nét tim bị che
- `cosmetic=True` trên tất cả nét ống — nếu đổi sang `False`, nét sẽ phình to khi zoom
- Logic chọn màu qua `PIPE_COLORS.get(edge_mat, DEFAULT_DARK)` — không hardcode màu

---

## 3. Primitive vẽ nét — `_add_pipe_line` dòng ~3107

**Signature:** `_add_pipe_line(x1, y1, x2, y2, color, width, data, cosmetic=True, z=5)`

**Không được sửa:**
- Tham số mặc định `cosmetic=True` — xem lý do ở mục 2
- `z=5` mặc định cho pipe lines — pipe phải dưới fittings (z=6) và dưới clash overlay (z=7)

---

## 4. Fitting Lookup — `nevis_library_index.json`

**File:** `D:\Nevis2.03\nevis_library_index.json` (577 entries, 0 missing paths tính đến 2026-06-20)

**Quy tắc fitting key:**
- Key format: `{size}x{branch_size}{material}-{type}` hoặc `{size}{material}-{type}`
- Ví dụ: `65x50DV-Y`, `65DV-LL`, `50TMP-45°`
- Khi ống chính = nhánh: chỉ dùng `{size}{mat}-{type}` (không có `x`)
- Khi giảm kích: `{main}x{branch}{mat}-{type}` — main luôn lớn hơn branch

**Debug:** Khi fitting không tìm thấy → `nevis_preview_fitting_debug.txt` ghi `missing=<key>`

---

## 5. Pipe Check — `_nevis_pipe_check_*` dòng ~25354–25700

Các hàm này kiểm tra BOM và kích thước ống trong dialog.
Không liên quan đến rendering — có thể sửa độc lập với mục 1–4.

---

## 6. Cách test sau khi sửa

```powershell
# 1. Chạy test suite (không cần GUI)
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py
# Kết quả mong đợi: 274 passed

# 2. Mở NEVIS, load temp.txt, set 主管サイズ=65, bấm 適用
# Kiểm tra: panel 材料/庫 bên phải hiện đúng DV-65/TMP-65/65x50 fittings
# Kiểm tra: các nét ống VP/DV = 5 nét, TMP = 7 nét
python -B D:\Nevis2.03\Nevis_no_ui.py
```

---

## Lịch sử thay đổi

| Ngày | Nội dung | Commit |
|------|----------|--------|
| 2026-06-20 | Xác nhận pipe/fitting OK sau session finish_layers. Không có thay đổi pipe code. | `c252046` |
| 2026-06 | Chốt NEVIS_PIPE_STYLE_LOCKED_VERSION — 5/7 nét, cosmetic, centerline pattern | (prior) |
