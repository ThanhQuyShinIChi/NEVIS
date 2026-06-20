# Elevation UI Integration Plan

Date: 2026-06-18
Status: Plan only - read-only preview, no Apply wiring

## Muc Tieu

Gan giao dien Elevation Preview voi model thuc cua NEVIS o che do read-only:

- Chay pipeline B1-B6.
- Hien thi summary va review rows.
- Cho phep chon row de highlight target tren ban ve.
- Khong mutate model va khong tham gia undo.

Ngoai pham vi:

- Apply Engine va Undo Transaction wiring.
- Ghi `Node.z`, `edge.start_z`, hoac `edge.end_z`.
- Save/open schema.
- BOM/JWW.
- Milestone C.

## 1. Vi Tri UI Phu Hop Trong `Nevis_no_ui.py`

### Hien trang

MainWindow da co khu vuc elevation trong selection/task panel:

- `g_pipe_elev`: controls metadata cao do cua pipe dang chon.
- `g_elevation_report`: bang report cao do hien tai.
- `btn_refresh_elevation_report`: tinh lai report hien tai.
- `table_elevation_report`: bang compact cao 130-175 px.

Task panel hien tai da day va gan chat voi drainage workflow. Mockup Elevation
Preview can bang rong, summary cards va nhieu rows, nen khong phu hop de chen
toan bo vao `g_elevation_report`.

### De xuat

Them mot nut moi trong `g_elevation_report`, dat cung hang voi nut tinh lai hien
tai hoac ngay ben duoi bang report:

- Internal widget name de xuat: `btn_elevation_dry_run`.
- Text phai qua language key, khong hard-code.
- Nut mo mot `QDialog` read-only, modeless.
- MainWindow giu reference `elevation_preview_dialog` de tranh mo trung nhieu
  dialog va de retranslate khi doi ngon ngu.

Dialog modeless duoc chon vi nguoi dung can click row va quan sat highlight tren
ban ve chinh. Khong dung full modal `exec()`.

Khong thay the hoac doi behavior cua:

- `btn_refresh_elevation_report`.
- `table_elevation_report` hien tai.
- Cac nut sua metadata/propagate elevation cu.
- Bat ky drainage, JWW, BOM control nao.

### Cau truc dialog toi thieu

- Window title: `self.tr("window_title")` hien huu.
- Header label: localized elevation preview title.
- Read-only badge.
- Nut localized dry run.
- Bon summary values.
- QTableWidget/QTableView read-only, single-row selection.
- Read-only footer.

Khong co Apply, OK-to-write, Save, hoac editable cell.

## 2. Nut Mo Elevation Preview

### Entry point

Nut moi trong elevation report group mo/reuse dialog:

```text
MainWindow.open_elevation_preview()
```

Behavior de xuat:

1. Neu dialog chua ton tai, tao mot instance va luu reference.
2. Neu da mo, raise/activate dialog hien tai.
3. Dialog ban dau co summary zero va bang rong, hoac tu chay dry run mot lan.
4. Nut dry run trong dialog la action duy nhat tao report moi.

De giu behavior de doan, khuyen nghi:

- Mo dialog khong tu mutate va co the chua chay pipeline.
- Nguoi dung bam nut localized dry run de tao/fresh report.
- Sau model edit, ket qua duoc danh dau stale va yeu cau chay lai.

Nut chi enable khi model co edge. Neu dang detail-preview/read-only mode co overlay
rieng, nut/row highlight phai theo gate hien tai de tranh hai preview mode xung
dot.

Khong goi `save_undo_snapshot()` khi mo dialog hoac dry run.

## 3. Cach Chay Pipeline B1-B6

### Public entry point

Dung public function hien co:

```python
report = build_proposal_review(self.model)
```

Function nay da chay noi tiep:

1. B1 Anchor Discovery.
2. B2 Wavefront Topology.
3. B3 Candidate Evaluation.
4. B4 Conflict & Lock Report.
5. B5 Propagation Proposal / Dry Run.
6. B6 Proposal Review Report.

UI khong tu lap lai logic B1-B6 va khong tu phan loai conflict/lock bang logic
rieng.

### Read-only contract

Truoc khi wiring, can co integration test chung minh:

- Model truoc/sau `build_proposal_review()` bang nhau.
- `Node.z` khong doi.
- `edge.start_z` va `edge.end_z` khong doi.
- Undo stack khong doi.
- Dirty/save state khong doi.

UI chi giu `ProposalReviewReport` va display mapping. Khong goi
`apply_elevation_review()`.

### Freshness

Moi lan bam dry run:

- Doc `self.model` hien tai.
- Tao report moi.
- Thay toan bo rows/summary cu trong dialog.
- Capture model identity va mot read-only signature toi thieu cho target pairs,
  orientation, endpoint Z/level, locks, va LevelDatum.

Khong reuse report sau:

- Open/new/scan thay `self.model`.
- Topology edit.
- Elevation metadata/LevelDatum edit.
- Undo thay full model object.

Neu dialog van mo sau model change, danh dau ket qua stale, clear highlight, va
yeu cau dry run lai. Khong silently highlight theo stale index.

### Error handling

Pipeline exception:

- Model giu nguyen.
- Clear/giu report cu theo policy da chon, nhung phai danh dau stale.
- Hien localized error text.
- Raw exception/reason code chi ghi diagnostic log, khong hien truc tiep tren
  UI.

## 4. Cach Hien Thi Summary

Nguon du lieu la `ProposalReviewReport.summary`:

- `proposed_count`.
- `blocked_by_conflict_count`.
- `blocked_by_lock_count`.
- `skipped_known_target_count`.

Bon summary item theo mockup:

- Proposed status -> blue.
- Conflict status -> red.
- Locked status -> amber.
- Skipped/known target -> gray.

Mau chi la secondary cue; moi item bat buoc co localized label va count de ho
tro accessibility.

Summary khong duoc tinh lai bang cach parse text hien thi. Neu backend summary
va row count khong khop, UI hien localized warning va khong sua report.

Khong hien raw backend status nhu `Proposed`, `Blocked by Conflict`, hoac code
`known_target`.

## 5. Cach Hien Thi Bang Ket Qua

### Columns

Bang read-only gom dung nam cot:

1. Type/status.
2. Target.
3. Current elevation.
4. Proposed elevation.
5. Reason.

Header text deu qua language key.

### Row mapping

Moi `ProposalReviewRow` tao mot table row. Store object/identity metadata trong
`Qt.UserRole`, khong suy identity tu display text.

Type:

- Map internal status/code sang language key.
- Style tag theo status color.
- Khong hien raw enum/code.

Target:

- Dung endpoint-pair identity va orientation da capture trong B6 row.
- Format localized: pipe + canonical pair + localized start/end.
- Khong dung `edge_index` lam user-facing identity.
- Vi du JP: `配管 2-3 / 開始`.
- Vi du VI: `Ống 2-3 / Bắt đầu`.

Current:

- Resolve theo cung semantics B1: explicit endpoint Z truoc, sau do LevelDatum.
- Unknown hien localized empty marker/em dash, khong hien chu `None`.
- Format number thong nhat voi elevation report hien tai.

Proposed:

- Chi hien `proposed_z` cho proposed row.
- Blocked/skipped row hien em dash.
- Khong tu tinh slope, offset, invert, hoac Milestone C value.

Reason:

- Map backend reason code sang language key.
- Khong hien raw English reason.
- Unknown reason hien localized generic warning; raw code chi duoc log.

### Read-only behavior

- `NoEditTriggers`.
- Single row selection.
- Sorting co the de sau; neu bat sorting, row metadata phai di cung item.
- Khong checkbox approve/apply.
- Double-click khong mutate va khong mo edit dialog.

## 6. Chon Dong Va Highlight Doi Tuong Tren Ban Ve

### Khong dung normal selection state

Khong khuyen nghi goi `MainWindow.select_edge()` khi chon preview row, vi method
nay:

- Doi `selected_edge`.
- Clear selected node/bushing.
- Cap nhat task panel va cac button workflow.
- Redraw normal selected-pipe highlight.

Day se lam Elevation Preview anh huong drainage selection workflow.

### Transient overlay de xuat

Tao mot overlay rieng trong `PreviewView`:

- Resolve edge bang endpoint pair + orientation tai thoi diem row selection.
- Zero match, multi-match, orientation mismatch, hoac stale signature: khong
  highlight; hien localized stale/ambiguous message.
- Lay toa do `edge.a`/`edge.b` tu `model.nodes`.
- Ve mot line overlay mau rieng, z-value cao hon pipe nhung khong thay
  `selected_edge`.
- Overlay khong nhan mouse event va khong tro thanh model item.
- Luu reference item de remove khi row doi, dialog dong, report refresh, model
  refresh, hoac language change neu can.

Internal state de xuat:

- `elevation_preview_highlight_item`.
- `elevation_preview_highlight_identity`.

Khong save state nay, khong dua vao undo, va khong dua vao JWW export.

### Canvas refresh

`PreviewView.draw_model()` clear/rebuild scene. Sau normal redraw:

- Overlay cu duoc xem la invalid.
- Dialog co the re-resolve current selected row va ve lai neu report van fresh.
- Neu model signature doi, clear overlay va mark stale.

Dong dialog luon clear overlay. Normal `selected_edge` highlight truoc/sau khi
mo dialog phai giu nguyen.

Center/zoom toi edge khong bat buoc cho ban toi thieu. Neu them sau, chi thay
viewport, khong thay selection/model.

## 7. Language Key, Khong Hard-Code English

### Policy

- Backend enum/reason code co the dung English internal code.
- UI khong bao gio hien truc tiep `row.status`, `row.reason`, exception code,
  hoac enum.
- Tat ca visible strings dung `self.tr(key)`/APP_TEXT hien huu.
- Window title dung `window_title` hien huu.

### Key groups can co

Ten key cu the co the chot khi implement, nhung can bao phu:

- Preview title.
- Dry-run button.
- Read-only badge/footer.
- Summary proposed/conflict/locked/skipped.
- Columns type/target/current/proposed/reason.
- Start/end/pipe target formatter.
- Moi B4-B6 reason code co the hien thi.
- Empty/no-results/stale/error messages.

Co the reuse key hien co khi dung nghia:

- `window_title`.
- `type`.
- `elevation_report_pipe`.
- `elevation_report_start`.
- `elevation_report_end`.
- `elevation_locked`.
- `elevation_calc_preview`.
- `elevation_warnings`.

Khong ghep cau bang raw English fragments. Với sentence/formatter, moi ngon ngu
can mot full template key de giu word order JP/VN.

### Status/reason mapping

UI adapter can co mapping explicit:

```text
internal status/code -> language key
```

Mapping phai exhaustive va co test. Vi du internal groups:

- proposed
- conflict
- locked
- skipped/known_target
- multiple_anchors
- candidate_conflict
- source_edge_locked
- target_edge_locked
- target_already_known

Unknown code khong duoc fallback thanh chinh code. Fallback phai la localized
generic text.

### Runtime language change

`MainWindow.refresh_language_texts()` phai goi
`elevation_preview_dialog.retranslate_ui()` neu dialog dang ton tai.

`retranslate_ui()` cap nhat:

- Dialog/window title.
- Header, button, badge, footer.
- Summary labels.
- Table headers.
- Tat ca visible status/target/reason cells tu internal row data.
- Empty/stale/error state.

Khong chay lai B1-B6 chi de doi ngon ngu. Dialog re-render report hien tai tu
internal data.

Manual check bat buoc: doi JP -> VI -> JP khi dialog dang mo, khong con text cua
ngon ngu truoc va khong xuat hien English enum/code.

## 8. Tranh Anh Huong Drainage Workflow

### Separation rules

- Them mot entry button rieng; khong repurpose existing elevation/drainage
  buttons.
- Dialog chi doc `self.model`.
- Khong goi Apply Engine.
- Khong goi `save_undo_snapshot()` hoac Undo Transaction API.
- Khong goi `apply_common()`, `rebuild_flow()`, hoac topology mutation.
- Khong thay `selected_node`, `selected_edge`, `selected_bushing_id`.
- Khong thay pending reducer/special-equipment state.
- Highlight la scene overlay tam, khong phai model/selection.
- Khong auto-save, khong thay project payload.
- Khong goi JWW/BOM export/build logic.

### Lifecycle safety

- Mo/dong dialog khong thay model.
- Dry run failure khong clear normal selection.
- MainWindow close se close/delete dialog va overlay.
- Open/new project se invalidate/close report cu.
- Undo model replacement se invalidate report cu.
- Detail preview/pending edit mode phai block highlight neu overlay co the xung
  dot voi readonly/ghost scene hien tai.

### Performance

Ban dau co the chay B1-B6 synchronous vi pipeline module-level nhe. Trong dry
run:

- Disable rieng nut dry run de ngan double click.
- Khong disable drainage controls lau hon thoi gian call.
- Restore button trong `finally`.

Neu graph lon lam UI freeze dang ke, worker-thread/snapshot design la scope
rieng. Khong dua thread vao minimal implementation ma chua co test thread-safe.

## 9. Tests Va Manual Checks

### Module/UI adapter tests

- `build_proposal_review(real_model)` khong mutate model.
- Summary mapping dung bon count.
- Moi B6 status map toi dung language key.
- Moi known reason map toi language key.
- Unknown status/reason khong leak raw English code.
- Target label dung pair/orientation, khong dung index.
- Current dung explicit Z/LevelDatum semantics.
- Proposed chi hien cho proposed rows.
- Empty report hien localized empty state.

### Dialog tests, co the chay Qt offscreen

- Dialog chi co dry-run action, khong co Apply.
- Table `NoEditTriggers` va single-row selection.
- Dry run khong goi Apply Engine/undo/save.
- Model deep-equal truoc/sau dry run.
- `Node.z`, `start_z`, `end_z` khong doi.
- JP render khong co English backend code.
- VI render khong co English backend code.
- Runtime JP/VI switch retranslate dialog dang mo.

### Highlight tests

- Chon row resolve dung endpoint pair/orientation.
- Overlay xuat hien tren dung pipe.
- Normal `selected_edge` khong doi.
- Doi row remove overlay cu va ve overlay moi.
- Zero match/multi-edge/orientation mismatch clear overlay va hien localized
  warning.
- Dong dialog va refresh model remove overlay.
- Overlay khong xuat hien trong save/JWW/BOM data.

### Regression tests

- Full `test_elevation*.py` PASS.
- Undo transaction tests PASS va dry run tao zero undo step.
- Drainage selection/edit/drag van hoat dong truoc va sau khi mo dialog.
- Existing compact elevation report van hoat dong.
- Detail preview readonly gate van hoat dong.
- Save/open payload khong thay doi.

### Manual checklist

1. Mo project co Proposed/Conflict/Lock/Skipped rows.
2. Ghi lai `Node.z`, endpoint Z, undo stack, selection.
3. Mo dialog va bam dry run.
4. Doi ngon ngu JP/VI trong khi dialog dang mo.
5. Chon tung loai row va kiem tra highlight.
6. Dong dialog; kiem tra overlay bien mat va selection cu con nguyen.
7. So sanh model/undo stack truoc sau.
8. Thu lai drainage select/edit/drag va detail preview.
9. Xac nhan khong co Apply, save/open, JWW/BOM side effect.

## Dieu Kien Hoan Thanh Read-Only Preview

Read-only Elevation Preview chi duoc coi la hoan thanh khi:

- UI chay B1-B6 va chi hien report.
- Khong model mutation va khong undo step.
- Summary/table dung.
- Highlight dung identity ma khong thay normal selection.
- JP/VI runtime retranslation PASS.
- Khong leak English backend code.
- Drainage, save/open, JWW/BOM regression checks PASS.

Hoan thanh preview khong tu dong cap quyen cho Apply wiring.
