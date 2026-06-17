# NEVIS Future Foundation Review

Ngay hien tai bao cao nay chi la phan tich kien truc. Khong co code nao duoc sua trong buoc nay.

Pham vi:

- Elevation Foundation
- Architecture Model Review
- Structure Model Review
- Clash Detection Foundation
- Section Generation Foundation
- PDF/Image Recognition Roadmap
- JWW Dependency Audit
- Future Technical Debt Report

Nguyen tac nen giu:

- NEVIS Engineering Model la nguon su that cuoi cung.
- JWW, DWG, DXF, PDF, Image Recognition chi la input/output hoac nguon nhan dang.
- Khong khoa NEVIS vao workflow JWW.
- Khong suy doan cao trinh, vat lieu, clash hoac section khi chua co du lieu ky thuat ro rang.
- Backward compatibility la bat buoc.

---

## 1. Elevation Foundation Deep Review

### 1.1 Trang thai source hien tai

Trong `Nevis_no_ui.py`, model hien tai da co cac field nen mong:

```python
class Node:
    id: int
    x: float
    y: float
    z: Optional[float] = None
    level_id: str = ""

class Edge:
    slope: Optional[float] = None
    vertical_type: str = "unknown"
    elevation_mode: str = "unknown"
    system_type: str = ""

class PipeModel:
    model_schema_version: int = 1
```

Save/open project hien tai da ghi/doc:

- `model_schema_version`
- `Node.z`
- `Node.level_id`
- `Edge.slope`
- `Edge.vertical_type`
- `Edge.elevation_mode`
- `Edge.system_type`

Dieu nay rat dung voi huong foundation: da co metadata, nhung chua doi behavior.

### 1.2 GL / SL / FL concept

De xuat dung cac khai niem sau:

| Concept | Giai thich | Vai tro |
|---|---|---|
| GL | Ground Level, cot mat dat | Moc ngoai nha, ha tang, san nen |
| SL | Slab Level, cot san ket cau | Lien quan dam, san, cot, clash voi ket cau |
| FL | Floor Level, cot san hoan thien | Moc nguoi dung hay doc tren ban ve kien truc |
| Custom Datum | Moc tuy bien | Tran, day dam, pit, basement, technical floor |

GL/SL/FL khong nen chi la text hien thi. Nen la `datum_type` co gia tri on dinh:

```text
GL
SL
FL
custom
```

Ten hien thi tieng Nhat/Viet nen nam o UI/language layer sau nay.

### 1.3 LevelDatum model

De xuat model nho nhat:

```python
@dataclass
class LevelDatum:
    id: str
    name: str = ""
    elevation_mm: float = 0.0
    datum_type: str = "FL"
    floor_index: Optional[int] = None
    description: str = ""
```

Y nghia:

| Field | Y nghia | Default |
|---|---|---|
| `id` | ID on dinh, vi du `GL`, `1F_FL`, `1F_SL` | bat buoc |
| `name` | Ten hien thi | `""` |
| `elevation_mm` | Cao trinh tuyet doi, don vi mm | `0.0` |
| `datum_type` | `GL`, `SL`, `FL`, `custom` | `FL` |
| `floor_index` | So tang neu co | `None` |
| `description` | Ghi chu | `""` |

Khong nen them qua nhieu field o buoc dau. Nhung field nhu building_id, zone_id, phase_id co the them sau khi NEVIS co Architecture/Structure Model.

### 1.4 Quan he giua Node.z va LevelDatum

De xuat:

```text
Node.z = cao trinh tuyet doi cua node, don vi mm
Node.level_id = tham chieu toi LevelDatum.id
```

Khong nen luu `Node.relative_z` trong buoc dau vi no tao du lieu trung lap. Khi can co the tinh:

```text
relative_z = Node.z - PipeModel.level_datums[Node.level_id].elevation_mm
```

Trang thai hop le:

| Node.z | Node.level_id | Y nghia |
|---|---|---|
| `None` | `""` | Project 2D cu, chua co cao trinh |
| `None` | `"1F_FL"` | Node thuoc level, nhung chua co cao trinh rieng |
| `12300.0` | `"1F_FL"` | Node co cao trinh tuyet doi va thuoc level |
| `12300.0` | `""` | Node co cao trinh nhung chua gan level |

Nguyen tac quan trong:

- `Node.z` la gia tri hinh hoc de tinh toan.
- `LevelDatum` la moc tham chieu de quan ly tang/cot.
- `level_id` la quan he logic, khong thay the cho `z`.

### 1.5 Tuong lai slope

Hien co `Edge.slope`. Chua nen tinh slope trong foundation.

De xuat y nghia ve sau:

```text
Edge.slope = do doc theo ti le hoac decimal, can chot format truoc khi dung
```

Can chot 1 format duy nhat:

| Option | Vi du | Uu diem | Rui ro |
---|---|---|---|
| Decimal | `0.02` | Tot cho tinh toan | Nguoi dung hay doc thanh 2% |
| Percent | `2.0` | De hien thi | De nham voi decimal |
| Ratio string | `"1/50"` | Giong thuc te Nhat | Kho tinh toan |

Khuyen nghi:

- Luu noi bo bang decimal: `0.02`.
- Hien thi UI bang `%` hoac `1/50`.
- Chua ap dung trong buoc foundation.

Tuong lai slope co the co:

```python
Edge.slope_mode: "unknown" | "manual" | "derived" | "flat" | "vertical"
```

Nhung hien tai da co `elevation_mode`; co the dung no truoc khi them field moi.

### 1.6 Tuong lai riser / vertical pipe

Hien co:

```python
Edge.vertical_type = "unknown"
```

De xuat y nghia tuong lai:

```text
unknown
horizontal
vertical
riser
drop
offset
```

Can phan biet:

- Vertical pipe: doan ong co vector z lon.
- Riser: ong dung lien tang hoac truc dung chinh.
- Drop: ong dung xuong cuc bo.
- Vent stack / drainage stack sau nay co the la subtype.

Chua nen auto detect riser. Vi ban ve 2D hien tai khong du thong tin cao trinh.

### 1.7 Data model de xuat cho foundation

Them toi thieu:

```python
@dataclass
class LevelDatum:
    id: str
    name: str = ""
    elevation_mm: float = 0.0
    datum_type: str = "FL"
    floor_index: Optional[int] = None
    description: str = ""
```

Them vao `PipeModel`:

```python
level_datums: Dict[str, LevelDatum] = field(default_factory=dict)
```

Khong them:

- `Node.relative_z`
- `Edge.start_z`
- `Edge.end_z`
- `StructureModel`
- `ArchitectureModel`
- slope calculation
- clash objects

### 1.8 Save/open strategy

Save project:

```json
{
  "model_schema_version": 2,
  "level_datums": {
    "GL": {
      "id": "GL",
      "name": "GL",
      "elevation_mm": 0.0,
      "datum_type": "GL",
      "floor_index": null,
      "description": ""
    }
  }
}
```

Open project cu:

- Neu thieu `level_datums`: dung `{}`.
- Neu node thieu `z`: dung `None`.
- Neu node thieu `level_id`: dung `""`.
- Neu edge thieu slope metadata: dung default hien tai.

Khong nen tu dong tao `GL` cho project cu neu nguoi dung chua nhap. Auto-create co the lam project 2D nhin nhu da co elevation.

### 1.9 Migration strategy

Migration nhe:

```text
if model_schema_version < 2:
    level_datums = {}
```

Khong sua node/edge cu.

Khong tinh lai flow.

Khong tao z mac dinh.

Khong doi BOM/JWW/preview.

### 1.10 Backward compatibility

Bat buoc:

- Project cu mo duoc.
- Save project moi ghi `level_datums`.
- Neu project moi mo bang code cu, cac field moi bi bo qua neu parser cu tolerant.
- Constructor dataclass phai dat field moi o cuoi de tranh loi positional constructor.

---

## 2. Architecture Model Review

### 2.1 Muc tieu dai han

Architecture Model se mo ta cac thanh phan kien truc anh huong den MEP:

- Wall
- Slab
- Beam
- Column
- Ceiling
- Shaft
- Opening

Hien tai chua implement. Chi nen thiet ke concept.

### 2.2 Minimum object set

#### Wall

Du lieu toi thieu:

```python
Wall:
    id
    level_id
    centerline/polyline
    thickness_mm
    height_start_z
    height_end_z
    fire_rating
    is_fire_compartment_boundary
```

Dung cho:

- pipe vs wall clash
- opening/sleeve
- fire compartment penetration
- section generation

#### Slab

```python
Slab:
    id
    level_id
    top_z
    bottom_z
    polygon
    thickness_mm
    structural_type
```

Dung cho:

- pipe vs slab clash
- sleeve/opening
- riser penetration
- FL/SL relationship

#### Beam

```python
Beam:
    id
    level_id
    centerline
    width_mm
    depth_mm
    bottom_z
    top_z
```

Dung cho:

- pipe vs beam clash
- clearance check
- section view

#### Column

```python
Column:
    id
    level_id
    footprint
    bottom_z
    top_z
```

Dung cho:

- pipe route avoidance
- clash detection

#### Ceiling

```python
Ceiling:
    id
    level_id
    elevation_z
    area_polygon
    ceiling_type
```

Dung cho:

- clearance
- pipe installability
- maintenance space

#### Shaft

```python
Shaft:
    id
    levels
    footprint
    bottom_z
    top_z
    shaft_type
    fire_rating
```

Dung cho:

- riser routing
- fire compartment
- vertical pipe coordination

#### Opening

```python
Opening:
    id
    host_type
    host_id
    shape
    center
    size
    level_id
    z_range
    purpose
```

Dung cho:

- sleeve/opening coordination
- pipe penetration validation

### 2.3 Khong nen them ngay vao 2.03

Khong nen implement cac object nay ngay trong buoc LevelDatum foundation. Ly do:

- Can UI, import, validation rieng.
- Co nguy co lam tang schema qua nhanh.
- Chua co source du lieu kien truc/ket cau on dinh.

Nen chi ghi trong thiet ke.

---

## 3. Structure Model Review

### 3.1 Geometry representation

Tuong lai clash detection can 3D geometry. Tuy nhien khong nen bat dau bang mesh phuc tap.

De xuat tang geometry:

| Geometry | Dung cho | Ghi chu |
|---|---|---|
| 2D polyline + z range | wall, beam path, shaft | de import tu CAD/PDF |
| 2D polygon + z range | slab, column, opening | tot cho clash co ban |
| bounding box 3D | clash nhanh | broad phase |
| exact solid simplified | clash chinh xac | narrow phase sau nay |

Minimum:

```python
Geometry3DRef:
    plan_shape
    z_min
    z_max
```

Chua can mesh/BREP.

### 3.2 Level relationship

Moi structure object nen co:

```text
level_id
z_min / z_max hoac top_z / bottom_z
```

Khong nen chi dua vao `level_id`. Clash detection can toa do z thuc.

### 3.3 Future clash requirements

Structure Model phai cung cap:

- volume 3D co the clash
- material/role neu can rule dac biet
- fire boundary metadata
- openings duoc phep
- tolerance
- source confidence neu lay tu PDF/Image recognition

---

## 4. Clash Detection Foundation

### 4.1 Pipe vs Pipe

Du lieu toi thieu:

- Pipe centerline 3D: start `(x,y,z)`, end `(x,y,z)`
- outer diameter
- insulation thickness neu co
- system_type
- clearance rule

Can:

```text
Node.z
Edge.size
pipe outer diameter table
Edge.system_type
```

Chua du:

- insulation
- exact pipe elevation mode
- vertical riser semantics

### 4.2 Pipe vs Beam

Can:

- pipe 3D cylinder simplified
- beam solid: width/depth/top/bottom
- level relationship
- allowed penetration/opening
- clearance/tolerance

Rui ro:

- Neu chi co 2D, rat de bao clash gia.
- Can z truoc khi clash.

### 4.3 Pipe vs Slab

Can:

- slab top/bottom z
- pipe z
- penetration point
- opening/sleeve data
- fire compartment rule neu slab la fire boundary

Rui ro:

- Drainage pipe co slope, nen z thay doi theo chieu dai.
- Khong the chi dung z tai node neu slope chua co.

### 4.4 Pipe vs Wall

Can:

- wall footprint/thickness/height
- pipe segment 3D
- opening/sleeve
- fire rating
- wall fire boundary flag

Lien quan:

- 防火区画貫通部
- 延焼防止

Khong nen tu dong validate neu chua co wall fire metadata.

### 4.5 Pipe vs Duct

Can:

- pipe centerline + OD
- duct route + width/height/elevation
- insulation
- clearance
- priority rule

Duct chua thuoc 2.03. Chi ghi nhan.

### 4.6 Clash data toi thieu

Sau nay can:

```python
ClashCandidate:
    id
    object_a_type
    object_a_id
    object_b_type
    object_b_id
    location_xyz
    severity
    rule_id
    clearance_required
    clearance_actual
    status
```

Nhung chua nen implement trong foundation dau tien.

---

## 5. Section Generation Foundation

### 5.1 Drainage profile

Can:

- pipe route order theo flow
- Node.z
- Edge.slope
- pipe size
- fitting type
- branch/main relationship
- level datum reference

Output tuong lai:

- profile line
- pipe invert/top/bottom
- slope annotation
- fitting marks

Chua nen generate neu `Node.z` va `Edge.slope` chua du.

### 5.2 Riser diagram

Can:

- vertical edges
- riser group id
- connected levels
- pipe size/material
- fitting at floor penetration
- shaft relationship

`Edge.vertical_type` se la field nen tang:

```text
unknown / vertical / riser / drop
```

Nhung chua nen auto detect.

### 5.3 Section view

Can:

- section cut line / plane
- objects intersecting plane
- pipe geometry 3D
- structure geometry 3D
- scale/orientation
- level markers

Du lieu toi thieu:

```python
SectionDefinition:
    id
    name
    cut_line_2d
    z_range
    view_direction
    level_ids
```

Chua nen implement trong LevelDatum foundation.

---

## 6. PDF Recognition Roadmap

### 6.1 Kien truc de xuat

Pipeline:

```text
PDF/Image
→ Raster/Vector Extraction
→ Drawing Layer Classification
→ Centerline Extraction
→ Symbol/Fitting Recognition
→ Text/OCR Recognition
→ Network Reconstruction
→ User Verification
→ Engineering Model
```

Nguyen tac:

- Recognition output khong duoc ghi thang thanh final model ma khong co confidence/user verification.
- Engineering Model moi la source of truth.
- Recognition phai luu source evidence de trace lai.

### 6.2 Data trung gian

De xuat:

```python
RecognizedPrimitive:
    id
    source_file
    primitive_type
    geometry
    confidence
    layer_hint
    text_hint

RecognitionCandidate:
    id
    candidate_type
    geometry
    inferred_properties
    confidence
    source_primitive_ids
    status
```

Status:

```text
pending
accepted
rejected
edited
```

### 6.3 Cac giai doan

#### Phase 1: Centerline extraction

- line detection
- snap endpoints
- graph reconstruction
- manual correction UI

#### Phase 2: Size/text recognition

- OCR pipe labels
- associate text with nearest line
- detect size/material

#### Phase 3: Fitting recognition

- symbol matching
- junction classification
- compare with topology

#### Phase 4: Preliminary BOM

- rough quantity
- missing library warnings
- user verification

#### Phase 5: Architecture/Structure recognition

- walls
- beams
- slabs
- columns
- openings

### 6.4 Rui ro

- PDF scan chat luong thap.
- Text Japanese/OCR sai.
- CAD layer khong chuan.
- Symbol nha thau khac nhau.
- Du lieu recognition khong nen duoc coi la truth ngay.

---

## 7. JWW Dependency Audit

### 7.1 Noi phu thuoc JWW ro rang

Trong `Nevis_no_ui.py`:

- `_read_jww_temp_entities`
- `parse_jww_temp`
- `parse_jww_background_geometry`
- `parse_jww_library_geometry`
- `load_temp`
- `open_temp`
- `_draw_jww_background`
- JWW style UI group
- `build_jww`
- `export_jww`
- `append_*_to_jww`
- `resolve_fitting_library_path_for_jww`
- `jww_attr`, `clean_jww_no`, `clean_jww_layer`
- output path `jwc_temp.txt`
- JWW line/color/layer settings

JWW hien dang vua la:

- input centerline source
- background drawing source
- library geometry format
- output target
- visual standard reference

Day la nguy co lock-in.

### 7.2 Noi da la engineering model

Da co cac thanh phan khong phu thuoc truc tiep JWW:

- `Node`
- `Edge`
- `Fitting`
- `PipeModel`
- `build_graph`
- `rebuild_flow`
- `classify_fittings`
- `edge_length`
- BOM rows
- project save/open `.nevis.json`

Tuy nhien `build_graph` hien van sinh tu JWW temp centerlines. Can tuong lai tach thanh:

```text
Input Adapter → Engineering Model Builder
```

### 7.3 Noi co nguy co khoa NEVIS vao JWW

Rui ro cao:

- Library geometry parser dang goi la JWW/TXT/JSON nhung nhieu transform rule van gan voi JWW axis.
- Preview va JWW export chia se nhieu correction rule dua tren JWW coordinate.
- UI dung `JWW` nhu workflow chinh.
- `temp.txt/jwc_temp.txt` la entry point chinh khi chay tu external transform.
- Ten helper `resolve_fitting_library_path_for_jww` dang duoc preview dung chung.

Khuyen nghi dai han:

- Doi concept thanh `GeometryLibraryResolver`.
- JWW exporter chi la mot exporter.
- JWW temp reader chi la mot importer.
- Preview dung Engineering Model + Geometry Library, khong dung ten JWW trong abstraction.

Khong nen refactor ngay trong 2.03 neu chua co test day du.

---

## 8. Future Technical Debt Report

### 8.1 Hotfix layers

Source hien tai co nhieu lop patch:

- V10, V11, V12...
- Bushing V3/V5
- Orphan connect V2-V6
- V36, V38, V40
- Special Equipment V1/V2/V11/V12
- V82-V111
- BOM canonicalization 2.03
- Profiling wrapper 2.03

Dac diem:

- Nhieu method duoc monkey patch bang `MainWindow.method = wrapper`.
- Nhieu wrapper long nhau.
- Behavior dung nhung kho truy vet.

Rui ro:

- Thu tu patch anh huong behavior.
- Mot method nhu `build_material_rows`, `draw_model`, `matching_library_path`, `open_project` co nhieu lop override.
- Khi them feature moi, de sua nham lop cu.

### 8.2 Duplicated logic

Vung lap logic:

- preview vs JWW transform
- fitting library path resolution
- material/family mapping
- BOM naming vs material label
- JWW geometry parsing vs JSON geometry parsing
- size normalization
- U/D/UP/DOWN handling

Khuyen nghi:

- Chua refactor lon ngay.
- Them test/golden output truoc.
- Khi refactor, tach theo module nho: BOM, library resolver, geometry transform, project IO.

### 8.3 Risky modules

Rui ro cao:

- `_draw_detailed_fittings`
- `build_jww`
- `resolve_fitting_library_path_for_jww`
- `matching_library_path`
- `build_material_rows`
- `load_temp/build_graph`
- `apply_common/apply_node`
- quick replace payload flow

Ly do:

- Lien quan truc tiep business rules.
- Preview/JWW/BOM phai dong bo.
- Nhieu hotfix da bao ve case thuc te.

### 8.4 Monolithic areas

`Nevis_no_ui.py` hien la monolithic file lon, gom:

- model
- parser
- UI
- preview
- BOM
- JWW export
- library engine
- hotfix layers
- profiling

Rui ro:

- Kho review.
- Kho test rieng.
- Kho onboarding.
- Kho them Architecture/Structure Model neu tiep tuc chen vao cung file.

Khuyen nghi dai han:

```text
nevis_model.py
nevis_project_io.py
nevis_bom.py
nevis_library.py
nevis_geometry.py
nevis_jww_import.py
nevis_jww_export.py
nevis_preview.py
nevis_validation.py
```

Nhung chi nen tach sau khi co test va golden outputs.

### 8.5 Future blockers

Neu khong xu ly dan, cac diem sau se chan vision dai han:

- No LevelDatum model.
- No Architecture/Structure model.
- JWW naming nam trong nhieu helper core.
- Display text van con tham gia logic o mot so noi.
- BOM/material family con bi tron giua pipe/fitting/display.
- Khong co abstraction cho 3D geometry.
- Khong co validation issue model.
- Khong co source confidence/evidence cho recognition.

---

## 9. Khuyen nghi uu tien sau bao cao

### Buoc tiep theo nen lam

`LevelDatum + PipeModel.level_datums + save/open metadata`

Pham vi:

- Them dataclass `LevelDatum`.
- Them `PipeModel.level_datums`.
- Save/open `level_datums`.
- Default `{}` khi project cu thieu.
- Tang `model_schema_version` len 2 neu anh dong y.

Khong lam:

- UI Level Manager.
- Auto z.
- Slope calculation.
- Riser detection.
- Structure/Architecture objects.
- Clash/Section.

### Ly do

Day la buoc nho nhat nhung co gia tri nen tang cao nhat:

- Mo duong cho GL/SL/FL.
- Khong doi behavior.
- Khong anh huong JWW/BOM/preview/fitting.
- Tuong thich voi `Node.z` va `level_id` da co.
- Khong khoa NEVIS vao JWW.

### Dieu can quyet dinh truoc khi implement

1. Co tang `model_schema_version` tu `1` len `2` khong?
2. Co auto tao datum mac dinh `GL` khong, hay de `{}`?
3. Don vi elevation chot la mm?
4. `LevelDatum.id` nen theo convention nao:
   - `GL`
   - `1F_FL`
   - `1F_SL`
   - `B1F_FL`
5. Co can `datum_type = "custom"` ngay tu dau khong?

Khuyen nghi cua toi:

- Tang schema len `2`.
- Khong auto tao GL cho project cu.
- Don vi noi bo: mm.
- Cho phep `datum_type`: `GL`, `SL`, `FL`, `custom`.
- `level_datums` default `{}`.

