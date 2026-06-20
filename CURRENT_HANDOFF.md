# NEVIS Current Handoff

Cap nhat: 2026-06-20 (Asia/Bangkok) — sau phien Task 22c + GL datum + Section refresh

## Doc truoc khi lam

1. Doc file nay.
2. Doc `SECTION_TEST_LOG.md` neu can lich su chi tiet va so lieu tung lan GUI test.
3. Chay `git status --short --branch` va `git log -10 --oneline`.
4. Khong ghi de thay doi dang co trong `CODEX_TASKS.md`.
5. Hoi nguoi dung truoc moi dot sua/commit/push.

## Repo va Git

- Repo dang lam: `D:\nevis2.03`.
- Branch: `feature/building-space-model`.
- Commit moi nhat: `a269faa` (Task 22 Clash Detection).
- Remote: `https://github.com/ThanhQuyShinIChi/NEVIS.git`.
- Da push len remote (18 commits ahead cua origin truoc phien nay; sau push da dong bo).
- Thay doi trong phien nay (chua commit): Task 22c UI + GL datum + Section refresh.

## Muc tieu san pham da thong nhat

- Mat bang va mat cat cung ton tai, dung chung model va sau nay cap nhat hai chieu.
- Mat cat phai dung kich thuoc/ty le that, phuc vu clash detection va xuat JWW.
- San cha va san giat cap la mot cau kien lien tuc, khong phai hai khoi mau khac nhau.
- Man hinh lam viec uu tien hinh hoc/mau ro; hatch chi tiet de danh cho profile xuat JWW.
- GL la datum bo sung cho tang 1, khong thay the SL.
- Clash Detection: ong MEP xuyen ket cau hien do, phat hien tu dong khi bam nut.

## Da hoan thanh trong phien nay (chua commit)

### Task 22c — Clash Detection UI

- `_nevis_run_clash_check(self)` monkey-patched vao `MainWindow.run_clash_check`.
- Adapter: `Edge` → `_PipeAdapter` voi `id=e.key`, `z_elevation = avg(start_z, end_z)`,
  `points = [(n1.x, n1.y), (n2.x, n2.y)]`.
- `self._clash_pipe_keys = set[str]` luu key cua ong bi clash.
- Nut `⚠ Kiem tra clash` mau do trong structural panel (compact layout, sau nut Mat cat).
- `paintEvent`: overlay do dam (`#dc1e1e`, 14px + `#ff5050`, 3px) tren ong co key trong `_clash_pipe_keys`, z=16/17 (tren highlight chon).
- `_clash_pipe_keys` la `getattr(mainwin, "_clash_pipe_keys", set())` — an toan neu chua chay.

### GL Datum bo sung

- Section render kiem tra `level_datums` co entry `datum_type="GL"` khong.
- Neu co: ve duong xanh la (`#64883c`) net dut-cham (`DashDotLine`) tai dung cao do `GL.elevation_mm` tinh tu SL±0.
- Nhan hien ten datum (VD "GL" hoac ten nguoi dung tu dat).
- Khong thay doi SL line — SL±0 van la datum chinh.

### Shared Section Refresh

- `PreviewView.draw_model` duoc monkey-patch: sau moi lan ve mat bang, neu section panel dang hien thi, schedule refresh mat cat qua `QTimer.singleShot(0)`.
- Debounce: chi mot refresh moi event loop cycle (`_section_refresh_pending` flag).
- Refresh giu nguyen zoom/pan (chi clear + re-render scene, khong `fitInView` lai).
- Khong refresh neu section chua mo hoac container da bi destroy.

## File da thay doi

- `Nevis_no_ui.py`: Task 22c overlay, GL datum, section refresh hook, clash check method, clash button.
- `modules/clash_detection.py`: da commit tai `a269faa`.
- `tests/test_clash_detection.py`: da commit tai `a269faa`.
- `CURRENT_HANDOFF.md`: file ban giao nay.
- `SECTION_TEST_LOG.md`: cap nhat them muc tieu da hoan thanh.

## Xac minh da chay

- Full suite: `274 passed, 38 warnings` — khong co regression.
- Lenh chay:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -q --ignore=tests/test_elevation_preview_ui.py --ignore=tests/test_node_z_edge_slope.py
```

## Trang thai GUI

- Chua retest GUI cho Task 22c, GL datum va section refresh.
- Can nguoi dung:
  1. Chay app: `python -B Nevis_no_ui.py`
  2. Ve san + san giat cap + ong MEP co cao do Z
  3. Bam `⚠ Kiem tra clash` trong panel Ket cau
  4. Xac nhan ong co clash hien do, status bar hien so luong
  5. Them GL datum trong panel Level Datums (type = GL, elevation = -300 chan. tang)
  6. Ve mat cat — xac nhan duong GL hien mau xanh la

## Viec tiep theo

1. Nguoi dung retest GUI (cac diem tren).
2. Commit + push sau khi xac nhan.
3. Kiem tra overlap display trong mat cat (con pending tu phien truoc).
4. JWW export profile (hatch, layer, net in) — dai han.

## Lenh tiep tuc nhanh

```powershell
cd D:\nevis2.03
git status --short --branch
git log -10 --oneline
python -B Nevis_no_ui.py
```

Khi debug GUI, khong xoa `section_debug.log`; dung session ID va timestamp de doi chieu thao tac.
