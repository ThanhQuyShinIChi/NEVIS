# NEVIS Current Handoff

Cap nhat: 2026-06-20 (Asia/Bangkok)

## Doc truoc khi lam

1. Doc file nay.
2. Doc `SECTION_TEST_LOG.md` neu can lich su chi tiet va so lieu tung lan GUI test.
3. Chay `git status --short --branch` va `git log -10 --oneline`.
4. Khong ghi de thay doi dang co trong `CODEX_TASKS.md`.
5. Hoi nguoi dung truoc moi dot sua/commit/push.

## Repo va Git

- Repo dang lam: `D:\nevis2.03`.
- Branch: `feature/building-space-model`.
- HEAD truoc cac thay doi chua commit: `6dce023` (Task 29f).
- Local dang ahead `origin/feature/building-space-model` 17 commit, behind 0.
- Remote: `https://github.com/ThanhQuyShinIChi/NEVIS.git`.
- Git da cai: `2.54.0.windows.1`.
- Chua commit/push cac thay doi trong phien nay.
- Nguoi dung yeu cau dong bo len Git sau khi cong viec da hoan thien va duoc xac nhan.

## Muc tieu san pham da thong nhat

- Mat bang va mat cat cung ton tai, dung chung model va sau nay cap nhat hai chieu.
- Mat cat phai dung kich thuoc/ty le that, phuc vu clash detection va xuat JWW.
- San cha va san giat cap la mot cau kien lien tuc, khong phai hai khoi mau khac nhau.
- Man hinh lam viec uu tien hinh hoc/mau ro; hatch chi tiet de danh cho profile xuat JWW.
- Task 22 Clash Detection lam sau khi workflow mat cat on dinh.

## Da hoan thanh trong phien nay

### Chan doan va do on dinh

- Them JSON Lines diagnostic log: `section_debug.log`.
- Log workspace, tao san, san giat cap, click duong cat, render, scene, splitter, fit va exception.
- Sua `QCursor` import.
- Gan `QGraphicsScene` vao `section_container`; mat cat khong con hien roi bien mat.

### Hinh hoc mat cat san

- `modules/section_view.py` co pure geometry:
  - `polygon_cut_intervals()`.
  - `build_unified_slab_sections()`.
  - `SectionSlabPiece`, `SectionOverlapBand`, `SectionSlabAssembly`.
- San cha bi cat bo trong core cua san giat cap.
- San thap keo vao san cha theo `overlap_width`.
- Renderer union cac piece thanh mot `QPainterPath` cung mau/net.
- Khong hatch, khong ve net dut overlap noi bo.
- Chi mot nhan loai San; cao do tung mat van co marker.

### Ty le va datum

- Mot `GEOMETRY_SCALE = 0.1 scene/mm` dung cho ca truc ngang va cao do.
- `fitInView` chi zoom dong nhat, khong lam meo ty le.
- Da do: san 6055mm -> 605.5 scene; overlap 500mm -> 50 scene; day 150mm -> 15 scene.
- Datum mac dinh la `SL±0`, khong phai `GL±0`.
- GL sau nay la datum bo sung cho tang 1, khong thay the SL.
- Reject duong cat ngan hon 10mm de tranh scene hang trieu don vi.

### Marker va section viewport

- Marker cao do la tam giac do chuc xuong, dinh cham dung mep duoc do.
- Marker san thap dung `core_start`, khong dung dau overlap extension.
- Text cao do dat ben phai marker (`±0`, `-100`, ...).
- Section viewport co wheel zoom tai chuot, limit 0.02..50.
- Left-drag pan bang `ScrollHandDrag`.
- Scene items khong chan thao tac pan.

### Sidebar Ket cau

- Panel rong 220px.
- 6 loai cau kien: 2 cot x 3 hang.
- Ve/Xoa: 2 cot.
- San giat cap va Mat cat: moi nut mot hang.
- Nhom truc: Them/Xoa 2 cot; doi prefix mot hang.
- Buoc bat/luoi mac dinh doi tu 303mm thanh 3mm.
- O nhap 3mm luon hien; combo preset cu an nhung giu de tuong thich.

### Responsive toolbar va checkbox

- Toolbar Xem ban ve chia 3 hang (compact) hoac 5 hang (narrow).
- Xem chi tiet / Hoan tac / Fit khong con phong rong bat thuong.
- Nut San giat cap legacy da an khoi toolbar.
- Nut Mat cat luon o sidebar sau resize.
- Them `Ico/checkmark.svg`.
- Checkbox checked co nen xanh va tick trang cho ca Hien nen/Hien luoi.

## File da thay doi

- `Nevis_no_ui.py`: renderer, diagnostics, section viewport, marker, sidebar va responsive toolbar.
- `modules/section_view.py`: pure unified slab-section geometry.
- `tests/test_section_view.py`: test scanline, parent replacement, overlap va toa do GUI that.
- `Ico/checkmark.svg`: tick trang cho Qt checkbox.
- `SECTION_TEST_LOG.md`: lich su chi tiet.
- `CURRENT_HANDOFF.md`: file ban giao nay.

## Xac minh da chay

- Test lien quan: `51 passed`.
- Full suite:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py
```

- Ket qua cuoi: `245 passed, 38 warnings`.
- `git diff --check` dat; chi co canh bao LF/CRLF cua Git.
- Warnings con lai la PySide signal disconnect va API `QMouseEvent.pos()` deprecated, chua gay fail.

## Trang thai GUI cuoi

- Nguoi dung da xac nhan sidebar/responsive/checkmark: `ok roi`.
- Phien GUI cuoi PID `19112`; tai thoi diem ban giao tien trinh da duoc nguoi dung dong.
- Anh smoke trong `%TEMP%`:
  - `nevis_unified_section_smoke.png`.
  - `nevis_section_marker_smoke.png`.
  - `nevis_structural_panel_compact_v3.png`.
  - `nevis_responsive_toolbar_1000_v2.png`.

## Viec tiep theo

1. Chot/commit/push lo thay doi mat cat + UI khi nguoi dung yeu cau.
2. Thiet ke shared selection/model refresh giua mat bang va mat cat.
3. Them cong cu edit phu hop trong mat cat, khong sao chep cach ve mat bang.
4. Them GL rieng cho tang 1 khi model co floor/level metadata.
5. Sau khi mat cat on dinh: Task 22 Clash Detection 2.5D.
6. Sau do: profile xuat JWW cho hatch/layer/net in.

## Lenh tiep tuc nhanh

```powershell
cd D:\nevis2.03
git status --short --branch
git log -10 --oneline
python -B Nevis_no_ui.py
```

Khi debug GUI, khong xoa `section_debug.log`; dung session ID va timestamp de doi chieu thao tac.
