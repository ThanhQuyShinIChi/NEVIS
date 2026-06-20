# Building Space Model Plan

Date: 2026-06-18
Status: Plan only - no implementation approved

## 1. Mục tiêu

Xây dựng một Building Space Model tối thiểu để NEVIS nhìn thấy không gian thi
công trước khi tiếp tục phát triển Elevation nâng cao.

Model phải đủ để trả lời các câu hỏi thực tế:

- Ống có va chạm ống khác không?
- Ống có đi xuyên sàn, dầm, cột, tường hoặc vách không?
- Ống có nằm ngoài khoang trần hoặc vùng được phép lắp đặt không?
- Khoảng hở thực tế có đủ cho bảo ôn, lắp đặt và bảo trì không?
- Vị trí xuyên kết cấu có nằm trong opening/sleeve/shaft được phép không?
- Một tuyến có thể thi công được, hay chỉ đúng về cao độ đường tim?

Building Space Model là dữ liệu nền cho collision và constructability. Nó không
phải BIM tổng quát, không thay thế phần mềm kiến trúc/kết cấu và không tự động
sửa tuyến ống.

## 2. Vì sao cần Building Space Model trước khi kiểm tra ống

`PipeModel` hiện tại mô tả graph đường tim ống trên mặt bằng, metadata kích
thước và một phần cao độ. `LevelDatum` chỉ cung cấp mốc Z. Hai loại dữ liệu này
không mô tả thể tích bị chiếm chỗ của công trình.

Chỉ biết X/Y/Z của đường tim không thể phân biệt:

- Va chạm thật với thiếu clearance.
- Xuyên sàn hợp lệ qua opening với xuyên sàn trái phép.
- Ống nằm dưới dầm với ống cắt qua dầm.
- Ống nằm trong khoang trần với ống đụng trần hoặc khung trần.
- Hai vật thể giao nhau trên mặt bằng nhưng tách nhau theo Z.
- Khoảng trống hình học với khoảng trống thực sự có thể lắp đặt/bảo trì.

Vì vậy Elevation chỉ nên là một thuộc tính đầu vào của envelope ống. Quyết định
"đi được hay không" phải dựa trên tương quan giữa pipe envelope và building
space.

## 3. Nguyên tắc thiết kế

1. Bắt đầu bằng 2.5D: footprint 2D cộng khoảng Z, chưa dùng mesh/solid BIM.
2. Dùng millimetre và cùng hệ tọa độ model hiện tại.
3. Tầng là container không gian; sàn là vật thể chiếm chỗ. Không đồng nhất hai
   khái niệm này.
4. Mọi entity có stable ID; index trong list không phải identity.
5. Hình học lưu theo dữ liệu gốc, envelope/query là dữ liệu suy ra.
6. Opening và vùng được phép là dữ liệu hạng nhất, không phải ghi chú text.
7. Geometry không hợp lệ phải bị từ chối hoặc báo rõ; không âm thầm sửa.
8. Collision engine chỉ đọc snapshot đã validate và không mutate model.
9. Thiếu dữ liệu phải tạo trạng thái `unknown/not_checked`, không được kết luận
   "không va chạm".
10. Model phải nhập được từng phần; không bắt người dùng dựng BIM đầy đủ trước
    khi nhận giá trị.

## 4. Ranh giới model

### 4.1 Quan hệ với model hiện tại

Đề xuất giữ Building Space Model thành module/domain riêng, sau đó project root
tham chiếu cả:

- `PipeModel`: graph ống, fitting, kích thước, vật liệu và elevation metadata.
- `BuildingSpaceModel`: tầng, cấu kiện, mặt hoàn thiện, opening và vùng clearance.
- `ProjectSettings`: đơn vị, tolerance, mapping level và rule set.

Không nhét polygon/solid trực tiếp vào `Node`, `Edge` hoặc `LevelDatum`.
`LevelDatum` có thể được tham chiếu bởi ID nhưng không sở hữu building entity.

### 4.2 Phạm vi tối thiểu

Các đối tượng bắt buộc cho phiên bản đầu:

- Floor/story.
- Slab/sàn bê tông.
- Drop slab/sàn giật cấp.
- Raised floor/sàn gỗ, sàn nâng.
- Wall/tường.
- Partition/vách.
- Beam/dầm.
- Column/cột.
- Ceiling/trần và vùng khung trần.
- Opening/sleeve/shaft dùng để cho phép xuyên.

Equipment và maintenance zone cần có trong data contract từ sớm nhưng có thể
triển khai sau nhóm cấu kiện bắt buộc.

## 5. Hệ tọa độ và quy ước hình học

### 5.1 Đơn vị

- X, Y, Z, thickness và clearance đều dùng `mm`.
- X/Y dùng đúng model coordinates, không dùng display coordinates đã flip/rotate.
- Z tuyệt đối dùng cùng datum với `Node.z`, `Edge.start_z/end_z` và
  `LevelDatum.elevation_mm`.
- Không lưu giá trị đã làm tròn theo UI vào model.

### 5.2 Footprint

Footprint tối thiểu là polygon khép kín gồm một outer ring và có thể có inner
rings. Phiên bản đầu chỉ hỗ trợ cạnh thẳng.

Validation bắt buộc:

- Ít nhất ba đỉnh phân biệt.
- Không self-intersection.
- Không cạnh zero-length.
- Ring khép kín theo quy ước serializer.
- Inner ring nằm trong outer ring và không chạm/cắt nhau ngoài tolerance.
- Diện tích lớn hơn geometry tolerance.

Canonical winding có thể được chuẩn hóa khi load/save, nhưng stable ID và tọa
độ người dùng không được thay đổi ngoài quy tắc đã công bố.

### 5.3 Khoảng Z

Mọi vật thể chiếm chỗ phải resolve được thành khoảng đóng:

```text
z_min <= z_max
```

Entity có thể nhập bằng absolute Z hoặc tham chiếu `LevelDatum` cộng offset.
Sau resolve, query snapshot luôn dùng absolute Z. Tham chiếu không tồn tại,
giá trị không finite hoặc khoảng đảo chiều là validation error.

### 5.4 Tolerance

Cần tách rõ:

- `geometry_tolerance_mm`: so sánh số và tiếp xúc hình học.
- `collision_tolerance_mm`: ngưỡng coi là giao nhau.
- `required_clearance_mm`: khoảng hở nghiệp vụ theo đối tượng/rule.

Không dùng một hằng số chung cho cả ba mục đích.

## 6. Data contract chung

Mọi building entity tối thiểu có:

- `id`: stable UUID/string, duy nhất trong project.
- `kind`: loại entity có enum đóng.
- `name`: tên hiển thị tùy chọn.
- `floor_id`: tầng sở hữu hoặc liên quan chính.
- `footprint`: polygon 2D, nếu entity dùng extrusion.
- `z_min`, `z_max` hoặc datum reference + offsets.
- `source`: manual/imported/derived và source reference tùy chọn.
- `enabled`: có tham gia query hay không.
- `properties`: metadata có schema, không dùng để thay geometry cốt lõi.

Mỗi entity cần trả về một `SpatialEnvelope` chuẩn hóa gồm:

- Stable entity identity và kind.
- Bounding box X/Y/Z để broad phase.
- Footprint hoặc primitive geometry cho narrow phase.
- Solid interval và các void/opening liên quan.
- Rule tags như structural, finish, penetrable, no-penetration.

## 7. Các đối tượng tối thiểu

### 7.1 Floor/story

Floor là container và phạm vi làm việc, không phải một slab mặc định.

Thông tin tối thiểu:

- Stable ID, tên và thứ tự tầng.
- Footprint phạm vi tầng.
- `base_datum_id` và `top_datum_id`, hoặc Z min/max rõ ràng.
- Mapping SL/FL dùng trong dự án.
- Trạng thái active/visible/checkable.

Một tầng có thể có nhiều slab, nhiều vùng giật cấp và chiều cao không đồng nhất.
Không suy ra slab chỉ từ `floor_id`.

### 7.2 Slab/sàn bê tông

Slab là polygon extrusion chiếm chỗ.

Thông tin tối thiểu:

- Footprint.
- Top Z và thickness, hoặc top/bottom Z.
- Structural/finish classification.
- Danh sách opening ID liên quan.
- Optional no-penetration tag.

Collision dùng slab solid trừ các opening hợp lệ. Mặt trên hoặc mặt dưới đơn lẻ
không đủ đại diện cho sàn.

### 7.3 Drop slab/sàn giật cấp

Drop slab không cần một geometry engine riêng. Nó là slab region có stable ID,
footprint và top/bottom Z riêng, liên kết với floor và có quan hệ tùy chọn với
slab nền.

Ranh giới giữa hai slab region phải kiểm tra overlap/gap và ưu tiên rõ ràng.
Không tự chọn slab theo thứ tự list khi hai vùng chồng nhau.

### 7.4 Raised floor/sàn nâng

Raised floor cần mô tả cả mặt hoàn thiện và khoang bên dưới:

- Footprint.
- Finished floor Z.
- Panel thickness.
- Underfloor void Z range.
- Support zone/post-grid envelope nếu có dữ liệu.
- Allowed route zone và forbidden zone tùy chọn.

Khoang rỗng không có nghĩa toàn bộ thể tích đều đi ống được. Khi chưa có support
geometry, kết quả constructability phải ghi rõ mức độ dữ liệu.

### 7.5 Wall/tường

Wall tối thiểu là center/baseline polyline có thickness và khoảng Z, được
normalize thành footprint extrusion.

Thông tin tối thiểu:

- Baseline hoặc footprint.
- Thickness.
- Bottom/top Z.
- Structural/non-structural classification.
- Opening liên quan.
- Penetration policy.

Wall có nhiều segment phải tạo envelope nhất quán tại corner; không chỉ dùng
bounding box cho narrow-phase collision.

### 7.6 Partition/vách

Partition dùng cùng primitive với wall nhưng là kind riêng vì rule xuyên, mức
độ nghiêm trọng và gợi ý xử lý khác nhau.

Thông tin bổ sung nên có:

- Partition system/type.
- Fire rating nếu biết.
- Service cavity nếu có.
- Allowed penetration policy.

### 7.7 Beam/dầm

Beam phiên bản đầu là extrusion của rectangular footprint hoặc swept rectangle
dọc baseline.

Thông tin tối thiểu:

- Footprint hoặc baseline + width.
- Bottom/top Z.
- Structural tag luôn rõ ràng.
- Opening/approved penetration chỉ khi được nhập explicit.

Không suy ra có thể khoan dầm chỉ vì pipe nhỏ. Mặc định penetration chưa được
phê duyệt là blocking conflict.

### 7.8 Column/cột

Column là footprint extrusion, hỗ trợ rectangle và polygon.

Thông tin tối thiểu:

- Footprint.
- Bottom/top Z.
- Structural classification.
- Optional clearance zone.

Column có thể xuyên nhiều floor; `floor_id` là ownership chính, nhưng spatial
query không được giới hạn chỉ theo floor nếu Z/X/Y thực sự giao nhau.

### 7.9 Ceiling/trần

Ceiling cần tách ít nhất hai khái niệm:

- Finished ceiling plane/surface.
- Ceiling support/plenum occupied or reserved zone.

Thông tin tối thiểu:

- Footprint.
- Finished ceiling Z.
- Support-zone Z range hoặc depth.
- Ceiling type và optional service openings.

Nếu chỉ biết mặt trần, NEVIS có thể kiểm tra pipe xuyên mặt trần nhưng không được
kết luận clearance với khung trần là an toàn.

### 7.10 Opening, sleeve và shaft

Opening là phép trừ hoặc vùng cho phép có chủ đích, không phải obstacle.

Thông tin tối thiểu:

- Stable ID và kind: slab opening, wall opening, sleeve hoặc shaft.
- Footprint/cross-section và Z range.
- Host entity ID khi có host cụ thể.
- Allowed systems/sizes tùy chọn.
- Required edge clearance và fill allowance tùy chọn.
- Approval/status metadata.

Một pipe giao slab/wall vẫn chỉ được coi là penetration hợp lệ nếu envelope nằm
trong opening theo tolerance và rule. Giao một phần hoặc thiếu edge clearance
phải là warning/conflict riêng.

## 8. Equipment và vùng không gian bổ sung

Giai đoạn sau cấu kiện tối thiểu cần thêm:

- Equipment body envelope.
- Installation clearance.
- Maintenance/access zone.
- Door/swing/removal path nếu cần.
- Reserved MEP corridor.
- No-route zone và preferred-route zone.

Equipment body và maintenance zone không được gộp: giao body là physical
collision, giao maintenance zone là constructability/access conflict.

## 9. Spatial query contract

Building Space Model phải cung cấp API đọc ổn định cho các engine sau này, thay
vì để collision code duyệt trực tiếp từng list entity.

Các query tối thiểu:

- Lấy entity/envelope theo stable ID.
- Lấy tất cả envelope giao một AABB X/Y/Z.
- Lấy floor/space candidates tại một điểm hoặc đoạn.
- Resolve Z range từ datum references.
- Lấy opening của một host hoặc vùng query.
- Lấy occupied, allowed và reserved zones trong một vùng.
- Trả diagnostic khi entity bị bỏ qua do invalid/incomplete data.

Query pipeline đề xuất:

1. Validate và normalize entity.
2. Tạo immutable/read-only query snapshot.
3. Broad phase bằng AABB/spatial index.
4. Narrow phase bằng footprint + Z interval.
5. Áp opening/void subtraction.
6. Áp clearance và constructability rules riêng.
7. Trả kết quả có identity, vị trí và bằng chứng định lượng.

Không tối ưu bằng spatial tree trước khi có benchmark. Contract phải cho phép
thêm index sau mà không đổi kết quả nghiệp vụ.

## 10. Quan hệ với pipe envelope

Building Space Model không sở hữu pipe geometry. Collision layer sẽ chuyển mỗi
đoạn ống thành envelope dựa trên:

- Centerline X/Y và profile Z dọc đoạn.
- Outside diameter.
- Insulation/protection thickness.
- Installation clearance theo rule.
- Fitting envelope tại node.

Cần giữ riêng ba lớp kết quả:

- `physical_collision`: solid pipe giao solid obstacle.
- `clearance_violation`: solid không giao nhưng khoảng hở không đủ.
- `constructability_conflict`: giao vùng bảo trì, vùng cấm hoặc penetration chưa
  được phê duyệt.

Đường tim pipe không được dùng trực tiếp để kết luận cả ba lớp trên.

## 11. Validation và chất lượng dữ liệu

Validation chạy ở ba cấp:

- Entity: ID, finite values, polygon và Z range hợp lệ.
- Relationship: floor/datum/host/opening reference tồn tại và đúng loại.
- Project: duplicate ID, vùng slab chồng mâu thuẫn, opening ngoài host, datum
  ambiguity và entity ngoài phạm vi hợp lý.

Mỗi issue cần có:

- Stable issue code.
- Severity: error/warning/incomplete.
- Entity IDs liên quan.
- Vị trí hoặc bounds nếu xác định được.
- Message key để UI dịch JP/VN.

Entity lỗi không được âm thầm biến mất khỏi kiểm tra. Snapshot phải báo danh
sách omitted entities; report tổng phải nói rõ phạm vi nào chưa được kiểm tra.

## 12. Persistence và schema migration

Building Space Model cần schema version độc lập với `PipeModel.model_schema_version`.

Đề xuất project payload có section riêng `building_space`, gồm:

- `schema_version`.
- `coordinate_system` và `length_unit` cố định/được validate.
- Floors.
- Building entities.
- Openings/zones.
- Project geometry/tolerance settings.

Yêu cầu persistence:

- Stable IDs giữ nguyên qua save/open và undo/redo.
- Load project cũ không có section này tạo model rỗng, không báo project hỏng.
- Unknown future fields được xử lý theo migration policy rõ ràng.
- Không serialize cache, AABB index hoặc envelope suy ra.
- Save-load-save không làm trôi số hoặc đổi thứ tự semantic.
- Invalid references được báo, không tự nối tới entity gần nhất.

Undo Transaction sau này phải snapshot Building Space Model cùng project state.
Không wiring persistence hoặc undo trong scope tài liệu này.

## 13. UX nhập và kiểm tra dữ liệu

Workflow tối thiểu nên theo thứ tự:

1. Chọn/tạo floor và gán SL/FL.
2. Vẽ hoặc import floor footprint.
3. Thêm slab và các vùng drop/raised floor.
4. Thêm beam, column, wall và partition.
5. Thêm ceiling/support zone.
6. Thêm opening/sleeve/shaft.
7. Chạy Building Space validation.
8. Hiển thị coverage và vùng thiếu dữ liệu.
9. Chỉ sau đó cho chạy pipe collision check trong phạm vi đủ dữ liệu.

Nguyên tắc UI:

- Nhập theo mặt bằng quen thuộc, thêm Z/thickness bằng form ngắn.
- Có preset nhưng mọi giá trị suy ra phải nhìn thấy và chỉnh được.
- Highlight entity và validation issue trực tiếp trên viewport.
- Phân biệt màu obstacle, opening, allowed zone và incomplete data.
- Không bắt nhập toàn bộ công trình để kiểm tra một floor hoặc selected area.
- Không hiển thị raw enum/code; dùng hệ thống ngôn ngữ JP/VN.

## 14. Lộ trình triển khai đề xuất

### Phase S0 - Chốt contract

- Chốt coordinate/unit/datum rules.
- Chốt stable ID và entity enums.
- Chốt polygon + Z interval primitives.
- Chốt opening/host semantics.
- Viết fixture JSON đại diện các trường hợp tối thiểu.

Deliverable: schema/spec và test fixtures, chưa có UI.

### Phase S1 - Geometry core read-only

- Data classes/domain module riêng.
- Polygon và Z validation.
- Entity normalization thành `SpatialEnvelope`.
- AABB broad-phase contract và deterministic query.
- Không tích hợp `Nevis_no_ui.py`.

Deliverable: module-level tests cho geometry/query.

### Phase S2 - Persistence và project adapter

- Section `building_space` có version.
- Backward-compatible load project cũ.
- Round-trip và migration tests.
- Tích hợp đúng ownership với Undo Transaction.

Deliverable: project có thể giữ Building Space Model mà chưa chạy collision.

### Phase S3 - Building Space editor/viewer

- Floor selection và visibility.
- Công cụ tạo/sửa entity tối thiểu.
- Overlay 2D và validation report.
- JP/VN runtime translation.

Deliverable: người dùng nhìn thấy và kiểm tra model không gian.

### Phase S4 - Pipe envelope và collision read-only

- Pipe/fitting envelope.
- Pipe-pipe và pipe-building physical collision.
- Opening subtraction.
- Clearance classification.
- Highlight vị trí va chạm, không mutate model.

Deliverable: report va chạm có vị trí và số đo.

### Phase S5 - Constructability rules

- Maintenance/reserved/no-route zones.
- Penetration approval rules.
- Gợi ý xử lý có giới hạn và giải thích được.
- Coverage/confidence report.

Deliverable: validation thi công, vẫn không tự động sửa tuyến.

### Phase S6 - Elevation-assisted routing

Chỉ sau khi S0-S5 ổn định mới dùng Building Space Model để đề xuất nâng/hạ,
đổi tuyến hoặc profile cao độ. Apply phải là scope/phê duyệt riêng và tuân thủ
identity, verify-before-write và Undo Transaction hiện có.

## 15. Chiến lược test

### Geometry unit tests

- Polygon hợp lệ, self-intersection, zero edge và inner ring sai.
- Datum + offset resolve đúng absolute Z.
- Touching, overlap và separation quanh tolerance.
- Wall/beam primitive normalize đúng footprint.
- Opening subtraction đúng và không áp nhầm host.
- Query deterministic, không phụ thuộc thứ tự list.

### Domain tests

- Floor không tự tạo slab.
- Drop slab overlap có diagnostic rõ ràng.
- Raised-floor void không bị coi là fully constructable khi thiếu support data.
- Ceiling plane-only trả coverage/incomplete đúng.
- Structural penetration mặc định block khi chưa có approved opening.
- Duplicate/missing/stale identity bị reject.

### Persistence tests

- Project cũ load với Building Space Model rỗng.
- Full round-trip giữ ID, geometry, references và precision.
- Invalid references không auto-remap.
- Schema migration có fixture cho từng version.
- Undo/redo giữ nhất quán PipeModel và Building Space Model.

### Integration tests sau này

- Pipe-pipe, pipe-slab, pipe-beam, pipe-wall/partition và pipe-ceiling.
- Giao footprint nhưng khác Z không báo physical collision.
- Đi trọn trong opening hợp lệ không báo collision.
- Đi lệch opening hoặc thiếu edge clearance báo đúng loại.
- Physical, clearance và constructability không bị gộp.
- Collision check không mutate pipe/building model và không tạo undo step.

## 16. Non-goals của phiên bản đầu

- BIM/IFC authoring đầy đủ.
- Mesh, curved/NURBS solid hoặc boolean CAD tổng quát.
- Phân tích kết cấu hay tự phê duyệt khoan/cắt cấu kiện.
- Mô phỏng trình tự thi công 4D.
- Tự động routing hoặc tự động Apply elevation.
- Đồng bộ hai chiều với Revit/IFC.
- Suy đoán geometry bị thiếu rồi báo kết quả như dữ liệu thật.

Import CAD/BIM có thể bổ sung sau. Dữ liệu import vẫn phải normalize vào cùng
domain contract và mang source/provenance rõ ràng.

## 17. Rủi ro cần chốt trước khi code

- Ý nghĩa Z hiện tại của pipe là tâm, đáy hay đỉnh ở từng workflow.
- Quy tắc SL/FL và datum theo dự án Nhật/VN.
- Polygon library và numerical robustness phù hợp môi trường đóng gói hiện tại.
- Cách biểu diễn wall corner và opening xuyên nhiều host.
- Ownership của floor-spanning entity.
- Mức dữ liệu tối thiểu để UI cho phép kết luận "PASS".
- Cấu trúc project root và migration từ payload `PipeModel` hiện tại.
- Undo scope khi sửa đồng thời datum và building entity.

Các mục này phải có quyết định và fixture cụ thể trong Phase S0; không để engine
tự chọn ngầm trong lúc implement.

## 18. Điều kiện hoàn thành Building Space Model nền tảng

Foundation chỉ được coi là hoàn thành khi:

1. Có schema versioned cho toàn bộ entity tối thiểu.
2. Floor và slab là hai khái niệm riêng, có test.
3. Mọi obstacle resolve được thành footprint + Z interval hợp lệ.
4. Opening/shaft/sleeve là entity có identity và host semantics rõ ràng.
5. Stable ID tồn tại qua save/open/undo; list index không dùng làm identity.
6. Spatial query deterministic và không mutate model.
7. Invalid/incomplete geometry luôn xuất hiện trong coverage diagnostic.
8. Project cũ vẫn load được.
9. Người dùng có thể highlight/kiểm tra entity và lỗi geometry trên viewport.
10. Chưa có collision nào được coi là PASS nếu vùng tương ứng thiếu dữ liệu.
11. Module/domain tests và persistence tests đều PASS.
12. Có review riêng trước khi bắt đầu Pipe Collision hoặc Elevation-assisted
    routing.

Tài liệu này không cấp quyền sửa `Nevis_no_ui.py`, wiring collision engine, hoặc
tiếp tục Apply/Elevation. Bước kế tiếp được phép chỉ là chốt Phase S0 và các test
fixture của Building Space Model.
