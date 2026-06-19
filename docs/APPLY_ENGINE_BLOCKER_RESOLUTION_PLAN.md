# Apply Engine Blocker Resolution Plan

Date: 2026-06-18
Status: Plan only - no wiring approved

## Scope

Tai lieu nay lap ke hoach giai quyet hai blocker truoc khi Apply Engine duoc
wiring vao `Nevis_no_ui.py`: edge identity va user-visible undo.

Quyet dinh da duoc duyet:

- Chua wiring Apply Engine vao `Nevis_no_ui.py`.
- Preview/apply khong dung `edge_index` lam identity.
- Dung endpoint-pair identity lam buoc trung gian.
- Verify toan bo truoc write.
- Multi-edge hoac mismatch la hard blocker.
- Khong partial apply va khong auto-remap.
- User-visible undo phai dung `save_undo_snapshot()` cua NEVIS.

Transaction snapshot trong Apply Engine van duoc dung de rollback loi write. No
khong phai user-visible Undo va khong tao undo stack rieng.

## Edge Identity Strategy

### Identity record

`edge_index` chi la metadata diagnostic hoac fast-path trong mot lan doc model.
Moi source/target edge trong preview can luu:

- `endpoint_pair`: `(min(a, b), max(a, b))`.
- `expected_a` va `expected_b`: orientation tai preview time.
- `target_endpoint`: `start` hoac `end`.
- `expected_target_node_id`: `expected_a` cho `start`, `expected_b` cho `end`.
- `preview_edge_index`: optional metadata, khong phai identity.

Canonical pair dung de tim edge hien tai. `expected_a`/`expected_b` giu
orientation vi `start_z` va `end_z` phu thuoc huong edge.

Neu preview edge la `(a=10, b=20, target=start)` nhung apply tim thay
`(a=20, b=10)`, canonical pair khop nhung orientation sai. Phai hard block;
khong duoc tu doi `start` thanh `end`.

Identity record phai duoc tao tu cung model state da sinh B6 report. Khong suy
endpoint pair tai apply chi tu stale `edge_index`. Source identity cung phai
duoc luu neu proposed Z phu thuoc source endpoint.

Endpoint pair la giai phap trung gian. Neu NEVIS sau nay ho tro parallel edges
giua cung hai node, model can stable edge ID truoc khi Apply Engine ho tro
topology do.

## Verify-Before-Write Rules

Verification phai chay cho toan bo apply plan truoc NEVIS undo snapshot va
truoc write dau tien. Bat ky loi nao cung reject toan bo.

### Model va edge

- Report phai thuoc dung model context da tao preview.
- Model khong bi thay the boi open/new/scan sau preview.
- Build endpoint-pair index moi tu `model.edges` tai apply time.
- Kiem tra uniqueness cua endpoint pair tren toan model.
- Khong co conflict, blocking warning, malformed row, hoac duplicate target.

Voi moi Proposed row:

1. Tim edge bang canonical endpoint pair, khong bang index.
2. Zero match: block `target_edge_missing`.
3. Nhieu match: block `multi_edge_endpoint_pair`.
4. Mot match nhung `(a, b)` sai orientation: block
   `edge_orientation_mismatch`.
5. Target endpoint phai van map toi `expected_target_node_id`.

Khong fallback sang nearest edge, selected edge, first match, hay sorted
orientation. Neu identity khop nhung index doi, co the resolve current index
moi; preview index chi de diagnostic.

### Relevant attributes

Voi target, verify lai:

- `elevation_locked` van `False`.
- Target `start_z`/`end_z` van unknown va bang preview old value.
- Target level ID van bang preview value.
- Target khong tro thanh known do LevelDatum thay doi.
- Endpoint-to-node mapping van dung.
- Proposed Z van finite numeric va bang gia tri da review.

Voi source, verify lai:

- Source endpoint pair ton tai duy nhat.
- Orientation, source endpoint, va endpoint-to-node mapping van khop.
- Source Z resolved van bang source Z luc preview.
- Source lock/conflict state khong lam proposal mat hieu luc.
- Level ID va `LevelDatum.elevation_mm` dung de resolve Z khong thay doi.

### Fresh report

Topology co the thay doi trong khi target attributes van giong. Giai phap trung
gian uu tien la build lai B1-B6 ngay truoc apply va so sanh identity/proposal
set voi report da review.

Neu fresh report khac reviewed report, hard block va yeu cau review lai. Khong
tu dong apply fresh report. Model-instance token chi la check bo sung vi no
khong phat hien in-place mutation.

Tat ca checks phai PASS truoc write dau tien. Khong partial mode, auto-resolve,
hay auto-remap. Engine van re-check lock va known value ngay truoc write.

## Multi-Edge Blocking Rules

Multi-edge la hai hoac nhieu edge co cung canonical endpoint pair, bat ke
orientation. Ca `(10,20)+(10,20)` va `(10,20)+(20,10)` deu la multi-edge.

Policy dau tien la strict va global:

- Scan toan bo `model.edges` truoc apply.
- Bat ky duplicate pair nao cung block toan bo apply.
- Khong chi block row target bi duplicate.
- Khong chon first/last edge va khong dung index de pha hoa.
- Khong merge, delete, hoac sua topology trong Apply Engine.

Global block can thiet vi duplicate pair co the lam sai topology va source
identity ngay ca khi no khong phai direct target.

Structured rejection can bao cao canonical pair, tat ca current indices,
orientation `(a, b)`, rows bi anh huong, va reason
`multi_edge_endpoint_pair`. Diagnostic chi de repair ben ngoai.

## Undo Integration Rule

### Ownership

- `save_undo_snapshot()` la owner duy nhat cua user-visible Undo.
- Apply Engine khong wiring `undo_elevation_apply()` vao UI.
- Compact engine snapshot chi phuc vu rollback va audit.
- Khong push ca compact undo va full-model snapshot cho cung operation.

### Sequencing khi wiring

1. Build/nhan reviewed B6 report.
2. Resolve endpoint-pair identities.
3. Verify model, multi-edge, identity, attributes, conflicts, va locks.
4. Dong bang verified apply plan.
5. Goi `save_undo_snapshot("apply_elevation_proposals")` dung mot lan.
6. Thuc hien Apply Engine transaction.
7. Thanh cong: refresh state/view va giu undo entry.
8. Write loi: engine rollback; operation khong duoc bao thanh cong.

Khong goi `save_undo_snapshot()` truoc verify, vi rejection khong duoc tao
ghost undo.

Wiring chi duoc phep khi co policy da test cho undo entry vua tao neu write loi
va rollback thanh cong. Model phai ve pre-apply state, undo history cu khong bi
mat, va khong co ghost successful-apply action.

Neu public undo API chua ho tro huy entry vua tao, can mot integration-level
transaction/undo API nho duoc review rieng. Apply Engine khong duoc thao tac
truc tiep `_nevis_undo_stack`.

## Tests Can Bo Sung Truoc Wiring

### Identity va multi-edge

- Resolve dung edge khi index doi nhung pair/orientation van khop.
- Reject edge bi xoa, index tro sai edge, pair doi, orientation dao, hoac target
  endpoint map sai node.
- Reject hai edge cung `(a,b)` va `(a,b)+(b,a)`.
- Multi-edge o source, target, hoac ngoai Proposed rows deu global block.
- Rejection report chua pair va tat ca matching indices.
- Moi case khong ghi `Node.z`.

### Attributes va stale report

- Target lock, Z, level ID, hoac LevelDatum thay doi sau preview.
- Source Z, source identity, orientation, lock, hoac conflict thay doi.
- Proposed Z bi sua, non-numeric, `NaN`, hoac infinity.
- Topology thay doi tao conflict moi.
- Fresh Proposed set tang, giam, hoac doi source.
- Moi mismatch reject truoc write va khong mutation.

### Transaction va undo

- Tat ca rows verify truoc first write.
- Nhieu rows apply all-or-nothing.
- Loi giua transaction va partial setter write deu rollback day du.
- Mismatch o row cuoi khong cho row dau bi ghi.
- Success goi `save_undo_snapshot()` dung mot lan, truoc first write.
- Validation/multi-edge failure khong save undo snapshot.
- Undo restore full model va selection.
- Failed write khong de ghost successful-apply undo entry.
- Apply Engine khong truy cap `_nevis_undo_stack`.

### Regression

- Full `test_elevation*.py` PASS.
- Real `PipeModel` contract tests PASS.
- `Node.z` va save/open schema khong thay doi.
- Khong UI hay Milestone C behavior trong blocker-resolution scope.

## Dieu Kien Duoc Phep Wiring `Nevis_no_ui.py`

Chi duoc wiring khi tat ca dieu kien sau dat:

1. Endpoint-pair identity/fingerprint contract da duoc review.
2. Review output co pair, orientation, target node, va relevant attributes.
3. Apply khong con dung index lam identity; index chi la metadata.
4. Verify-before-write la all-or-nothing tren toan plan.
5. Zero/multi-match, orientation/attribute/fresh-report mismatch deu hard block.
6. Global multi-edge scan va structured diagnostic co test.
7. Real `PipeModel`, stale report, va rollback tests PASS.
8. Undo ownership chi thuoc `save_undo_snapshot()`.
9. Undo sequencing va failed-write/ghost-entry policy co test.
10. Full elevation suite PASS.
11. Co phe duyet rieng de sua `Nevis_no_ui.py`.

Neu thieu bat ky dieu kien nao, safe baseline la B1-B6 read-only, Apply Engine
module-level only, va `Nevis_no_ui.py` khong import/call engine.

## Thu Tu Thuc Hien De Xuat

1. Dinh nghia endpoint-pair identity/fingerprint data contract.
2. Them identity resolution va global multi-edge detector o module level.
3. Them verify-before-write API khong mutate.
4. Cap nhat Apply Engine de consume verified identity, khong identity bang
   index.
5. Them identity, mismatch, multi-edge, stale report, va rollback tests.
6. Chay full elevation suite va review blocker resolution.
7. Thiet ke/test NEVIS undo adapter dung `save_undo_snapshot()`.
8. Xin phe duyet rieng truoc khi wiring `Nevis_no_ui.py`.

Khong buoc nao trong tai lieu nay tu dong cap quyen cho buoc 8.
