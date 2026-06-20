# NEVIS MEP — Bàn giao phiên làm việc 2026-06-20

Repo: `https://github.com/ThanhQuyShinIChi/NEVIS.git`
Branch: `feature/building-space-model`
Commit mới nhất: `42f9223`

---

## Trạng thái hiện tại

Tất cả thay đổi đã commit và push. Chạy app bằng:
```
python D:\Nevis2.03\Nevis_no_ui.py
```

---

## Những gì đã hoàn thành trong session này

1. **Wall junction merge** — RC/cột/dầm chồng nhau tự hợp thành 1 outline; LGS merge trong cùng preset. Sửa lỗi `QPainterPath` import.

2. **Màu + nét visual** — Tất cả pen 1px. Màu riêng từng loại trên cả mặt bằng lẫn mặt cắt. Label chỉ hiện khi click chọn.

3. **Sàn giật cấp** — Mặt bằng: màu vàng = vùng hạ xuống (nhìn từ trên), cam hatch = vùng chồng lấn gia cố (z=9, không che vách). Mặt cắt: `overlap_bands` từ `build_unified_slab_sections` giờ được render thành cam hatch tại ranh giới stepped.

4. **Đáy tường theo sàn giật cấp** — `_wall_bottom_segments` chia tường thành đoạn, mỗi đoạn đáy = `min(bottom_elevation, slab_top_tại_vị_trí)`.

5. **Right-click picker** — Click phải trên vùng nhiều đối tượng chồng nhau hiện danh sách; chọn tên để select đúng phần tử.

6. **Hướng nhìn mặt cắt** — Flip trái/phải theo hướng nhìn: axis=X+side=above (nhìn Nam) và axis=Y+side=right (nhìn Tây) thì flip.

7. **Bug fixes** — `UnboundLocalError: _etype` trong section render; `UnboundLocalError: etype` trong elevation dialog; `TypeError: int(None)` trong `find_element`; `RuntimeError: C++ object deleted` trong cut marker.

---

## Việc còn dang dở

- **PERF timing log tạm** vẫn còn trong `apply_common` (~line 8671-8678) — xóa sau khi user xác nhận freeze đã hết.
- **Performance freeze** (đổi main pipe size): fix đã áp dụng (rglob chạy background thread, throttle 120s) nhưng **chưa được user xác nhận** là hết hoàn toàn trên GUI thật.
- **Bug: stepped slab biến mất sau khi sửa parent** — chưa reproduce được, cần project + các bước cụ thể nếu còn xảy ra.

---

## Quy tắc bắt buộc

- KHÔNG commit/push khi user chưa yêu cầu rõ ràng.
- KHÔNG chạm pipe rendering khi chưa đọc `PIPE_CODE_LOCKED.md`.
- KHÔNG để `rglob()` chạy trong `draw_model()`.
- KHÔNG ghi đè `CODEX_TASKS.md` khi chưa đọc trước.
