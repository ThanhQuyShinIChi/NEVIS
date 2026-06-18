# Pipe Quick Check Plan

Date: 2026-06-18
Status: Kế hoạch tính năng (active, P1)

Tính năng "Kiểm tra dữ liệu ống nhanh" (Quick Check). Mục tiêu: dùng được
ngay trên NEVIS hiện tại, không cần Building Space Model, không cần cao độ
sàn/dầm/trần.

Đây là bước thực thi cụ thể của mục 2.1–2.2 trong
[NEVIS_INCREMENTAL_DELIVERY_PLAN.md](NEVIS_INCREMENTAL_DELIVERY_PLAN.md).

---

## 1. Vì sao làm Quick Check trước

### 1.1 Đây là nhóm lỗi kiểm được mà không cần xây thêm hạ tầng

Trong danh mục 20 lỗi thi công, nhóm C (#17–#20) và một phần kiểm tra dốc
phát hiện được chỉ bằng dữ liệu NEVIS *đang có hôm nay*: topology, cỡ ống,
vật liệu, fitting, thư viện, BOM. Không cần biết tầng, sàn, dầm, trần.

### 1.2 Giá trị thấy được ngay, đúng tinh thần incremental

Người dùng bấm một nút, thấy danh sách lỗi, click để nhảy tới ống lỗi. Đây
là kết quả nhìn thấy được trong vài ngày, không phải pipeline nhiều tuần.

### 1.3 Xây nền UX cho mọi cảnh báo về sau

Cơ chế "danh sách lỗi → click → zoom + highlight" làm đúng một lần ở Quick
Check sẽ dùng lại cho clash detection, cảnh báo cao độ, mọi cảnh báo tương
lai. Làm nhóm dễ trước để chốt đúng cách hiển thị lỗi.

### 1.4 Tránh lặp lại sai lầm Elevation

Elevation xây pipeline ghi Z nhiều tuần mà người dùng chưa bấm được gì. Quick
Check ngược lại: chỉ đọc dữ liệu đã có, chỉ báo lỗi, không ghi đè model, không
bắt nhập gì mới. Rủi ro thấp nhất, giá trị thấy sớm nhất.

---

## 2. Những dữ liệu NEVIS hiện đã có

Quick Check chỉ được dùng dữ liệu đã tồn tại, không yêu cầu dữ liệu mới:

- Graph topology: node (fitting/thiết bị/endpoint) và edge (đoạn ống).
- Hướng dòng chảy đã dựng (rebuild flow).
- Cỡ ống của từng đoạn.
- Vật liệu / loại hệ thống của từng đoạn.
- Phân loại fitting (LT, Y, DT, DL, LL, IN, 45, CO, 集合管...).
- Hệ 8 hướng (0/45/90/135/180/225/270/315°).
- Chiều dài đoạn ống.
- Thư viện vật tư (JSON/TXT): cỡ và chủng loại hợp lệ.
- Bảng BOM dựng từ model.
- Tọa độ mặt bằng của mọi đối tượng (để zoom/highlight).

Những dữ liệu KHÔNG có ở bước này, và Quick Check KHÔNG được giả định:
cao độ thật từng đoạn, sàn, dầm, trần, thiết bị, envelope 3D.

---

## 3. Những lỗi kiểm được ngay (phạm vi P1)

### 3.1 Cỡ / vật liệu ống không có trong thư viện

- So cỡ và vật liệu của từng đoạn với thư viện hiện hành.
- Báo đoạn nào dùng cỡ/vật liệu không tồn tại trong thư viện.
- Theo nguyên tắc đã chốt: thư viện là nguồn sự thật; cái gì không có trong
  thư viện thì không hợp lệ.

### 3.2 Fitting không hợp lệ về hình học

- Kiểm góc đấu nối có nằm trong hệ 8 hướng không.
- Kiểm tổ hợp cỡ/góc của fitting có tồn tại trong thư viện không.
- Báo fitting không có phụ kiện thật khớp, hoặc góc ngoài hệ cho phép.

### 3.3 BOM lệch với bản vẽ / model

- Dựng lại BOM từ model hiện tại và so với BOM đang hiển thị/xuất.
- Báo nếu có chênh lệch về số lượng, cỡ, hoặc chủng loại.
- Đây là kiểm tra "screen = BOM" — phải tiến tới bằng không.

### 3.4 Độ dốc dạng 1/N (không dùng % làm input chính)

- Mọi nơi nhập/hiển thị dốc trong Quick Check dùng `1/N` làm dạng chính.
- Nếu một đoạn có dốc đã ghi, hiển thị dưới dạng `1/N`.
- Nếu dốc nhập sai dạng (không phải `1/N` hợp lệ), báo lỗi định dạng.
- Phần trăm chỉ hiện như giá trị quy đổi phụ, không phải ô nhập chính.
- Lưu ý phạm vi: ở P1 chỉ kiểm *định dạng và tính hợp lệ của giá trị dốc đã
  có*, CHƯA kiểm "dốc đủ/không đủ theo cỡ ống" vì việc đó cần profile cao độ
  — để bước sau.

### 3.5 Click lỗi để zoom tới đối tượng

- Mỗi dòng lỗi gắn với một đối tượng cụ thể (đoạn ống hoặc fitting).
- Click dòng lỗi → viewport di chuyển và phóng tới đúng đối tượng, highlight.
- Đây là yêu cầu bắt buộc của P1, không phải tuỳ chọn.

---

## 4. UI tối thiểu cần có

Càng ít càng tốt. Không thêm cửa sổ phức tạp.

- **Một nút "Kiểm tra nhanh"** ở vị trí dễ thấy trong workflow hiện tại.
- **Một bảng kết quả** dạng danh sách, mỗi dòng gồm:
  - Mức độ (màu): lỗi / cảnh báo.
  - Loại lỗi (dùng đúng ngôn ngữ JP/VN đang chọn).
  - Mô tả ngắn, một dòng, nói rõ đối tượng nào.
- **Click dòng → zoom + highlight** đối tượng tương ứng trên bản vẽ.
- **Bộ đếm tổng** (ví dụ: 3 lỗi, 5 cảnh báo) để biết tình trạng tổng quát.

Không cần ở P1: bộ lọc nâng cao, xuất báo cáo, lưu lịch sử kiểm tra, gợi ý
tự sửa. Có thể thêm sau nếu thực sự cần.

---

## 5. Kết quả người dùng nhìn thấy

- Mở một bản vẽ thoát nước hiện có, bấm "Kiểm tra nhanh".
- Trong vài giây, hiện danh sách lỗi rõ ràng bằng ngôn ngữ đang chọn.
- Thấy ngay đoạn nào dùng cỡ lạ, fitting nào không khớp, BOM có lệch không.
- Click một dòng → màn hình nhảy tới đúng ống/fitting đó, được làm nổi bật.
- Sửa xong, bấm kiểm tra lại, lỗi đó biến mất khỏi danh sách.

Giá trị cảm nhận được: phát hiện lỗi trước khi phát hành bản vẽ, thay vì để
giám sát hoặc công trường phát hiện.

---

## 6. Điều kiện hoàn thành

P1 coi là xong khi tất cả các câu sau đều đúng:

1. Mở một bản vẽ có một đoạn dùng cỡ không có trong thư viện → Quick Check
   báo đúng đoạn đó.
2. Mở một bản vẽ có fitting góc ngoài hệ 8 hướng (hoặc tổ hợp cỡ/góc không
   có trong thư viện) → Quick Check báo đúng fitting đó.
3. Tạo một trường hợp BOM lệch model → Quick Check phát hiện chênh lệch; khi
   model và BOM khớp → không báo lệch.
4. Nhập độ dốc `1/100` → chấp nhận và hiển thị lại `1/100`; nhập một giá trị
   dốc sai định dạng → báo lỗi định dạng.
5. Click bất kỳ dòng lỗi nào → màn hình zoom tới và highlight đúng đối tượng;
   click dòng khác → nhảy tới đối tượng khác.
6. Bản vẽ không có lỗi → Quick Check báo "không có lỗi", không báo lỗi giả.
7. Chạy Quick Check KHÔNG làm thay đổi model, BOM, hay JWW output (read-only).

---

## 7. Test / manual check

### 7.1 Bộ bản vẽ mẫu cần chuẩn bị

Chuẩn bị sẵn vài bản vẽ nhỏ để kiểm bằng tay mỗi lần sửa:

- Bản vẽ "sạch": không lỗi → kỳ vọng danh sách trống.
- Bản vẽ "cỡ lạ": một đoạn cỡ/vật liệu ngoài thư viện.
- Bản vẽ "fitting sai": một góc ngoài hệ 8 hướng.
- Bản vẽ "BOM lệch": tạo lệch có chủ đích.
- Bản vẽ "dốc": vài tuyến có dốc `1/N` hợp lệ và một giá trị sai định dạng.

### 7.2 Cách kiểm bằng tay mỗi ngày

- Mở từng bản vẽ mẫu, bấm Quick Check, đối chiếu với kết quả kỳ vọng.
- Với mỗi lỗi báo ra: click thử, xác nhận zoom tới đúng đối tượng.
- Sau khi sửa lỗi trên bản vẽ mẫu, kiểm lại để chắc lỗi biến mất.

### 7.3 Kiểm tra không phá cái đang đúng

Sau mỗi lần thay đổi, xác nhận lại đường sống còn của NEVIS không đổi:

- Drainage workflow vẫn vẽ và cập nhật như cũ.
- BOM xuất ra như cũ (Quick Check chỉ đọc, không sửa).
- JWW export như cũ.
- Screen = BOM = JWW vẫn khớp.

### 7.4 Tự kiểm có đi lạc không (theo 5 câu cuối ngày)

- Nhìn thấy được chưa? Có nút và bảng kết quả trên màn.
- Người dùng được lợi gì? Phát hiện lỗi trước khi phát hành.
- Có phá cái đang đúng không? Drainage/BOM/JWW không đổi.
- Có bắt nhập thừa không? Không nhập Z, không nhập tầng/sàn.
- Điều kiện hoàn thành còn rõ không? 7 câu ở mục 6 vẫn kiểm được.

---

## 8. Ngoài phạm vi P1 (ghi rõ để khỏi trượt)

KHÔNG làm trong bước này, dù có thể bị cám dỗ:

- Building Space Model (tầng/sàn/dầm/trần).
- Kiểm dốc đủ/không đủ theo cỡ ống (cần profile cao độ → bước sau).
- Clash detection (ống–ống, ống–kết cấu).
- Apply Engine.
- Level Manager.
- Nhập cao độ Z từng đoạn.
- Gợi ý tự động sửa lỗi.

Các lỗi nhóm A/B trong danh mục 20 lỗi sẽ tới sau, khi có mô hình tầng/sàn
tối thiểu. Quick Check chỉ lo nhóm kiểm được bằng dữ liệu hiện tại.
