# NEVIS Incremental Delivery Plan

Date: 2026-06-18
Status: Kế hoạch cập nhật thực chiến (active)

Tài liệu này KHÔNG thay thế roadmap 12 tháng. Nó chuyển roadmap đó thành các
bản cập nhật nhỏ, làm được trong ngày/tuần, dùng được ngay.

Roadmap trả lời "đi đâu". Tài liệu này trả lời "hôm nay làm gì để người dùng
thấy NEVIS tốt hơn ngày hôm qua".

---

## 0. Năm quy tắc bất biến

Mọi bản cập nhật phải qua được cả 5 cửa này trước khi bắt đầu:

1. **Nhìn thấy được.** Sau khi làm xong, mở NEVIS lên là thấy khác. Nếu không
   nhìn thấy gì, đó là hạ tầng, không phải update.
2. **Nhanh hơn hoặc ít sai hơn.** Mỗi update phải trả lời được: nó tiết kiệm
   thao tác nào, hoặc nó chặn lỗi nào. Không trả lời được thì hoãn.
3. **Không hạ tầng dài ngày không kết quả.** Nếu một việc cần hơn 3 ngày mới
   thấy kết quả trên màn hình, phải cắt nhỏ lại cho đến khi mỗi mẩu thấy được.
4. **Không lặp lại sai lầm Elevation.** Elevation sai vì xây pipeline B1→B6 +
   Apply Engine trong nhiều tuần mà người dùng chưa bấm được nút nào. Cấm xây
   "nền tảng để sau này dùng" mà bản thân nó không dùng được ngay.
5. **Điều kiện hoàn thành cụ thể.** Mỗi bước phải có một câu kiểm tra dạng
   "mở NEVIS, làm X, thấy Y". Không có câu đó thì bước chưa được định nghĩa.

---

## 1. Tuần này

Mục tiêu tuần: người dùng mở NEVIS thấy ngôn ngữ đúng và làm việc với độ dốc
theo cách thực tế (1/N). Đây là việc nhỏ, rủi ro thấp, giá trị thấy ngay.

### 1.1 Sửa lỗi ngôn ngữ UI

- Rà soát các chuỗi hiển thị sai/lẫn ngôn ngữ trên giao diện hiện tại.
- Ưu tiên màn hình người dùng gặp nhiều nhất: thanh công cụ thoát nước, bảng
  vật tư, hộp thoại thay fitting.
- Mỗi ngày sửa một nhóm màn hình, không gom cả tuần rồi mới kiểm.

Điều kiện hoàn thành: mở NEVIS, chuyển ngôn ngữ JP và VN, mọi nhãn trên các
màn hình chính hiển thị đúng ngôn ngữ đã chọn, không còn chuỗi lẫn ngôn ngữ
hay chuỗi trống.

### 1.2 Độ dốc dạng 1/N

- Mọi nơi nhập và hiển thị độ dốc phải dùng `1/N` làm dạng chính.
- Phần trăm/decimal chỉ là giá trị phụ, có thể hiện nhỏ bên cạnh, không phải
  ô nhập chính.
- Giá trị mặc định theo thói quen thoát nước (ví dụ 1/50, 1/100).

Điều kiện hoàn thành: mở NEVIS, ở chỗ nhập độ dốc gõ `1/100`, hệ thống chấp
nhận và hiển thị lại `1/100`; không bắt người dùng quy đổi sang phần trăm.

---

## 2. Tuần sau

Mục tiêu tuần: người dùng phát hiện dữ liệu ống có vấn đề nhanh hơn, và đi
đến đúng đoạn ống lỗi bằng một cú click.

### 2.1 Kiểm tra dữ liệu ống nhanh

- Một lệnh "kiểm tra dữ liệu" chạy nhanh trên model hiện tại.
- Phát hiện các vấn đề rõ ràng, không cần cao độ: ống thiếu kích thước, kích
  thước không có trong thư viện, fitting không hợp lệ, đoạn ống cụt, nhánh
  không nối.
- Kết quả là một danh sách ngắn, mỗi dòng nói rõ vấn đề và thuộc đoạn nào.

Điều kiện hoàn thành: mở một bản vẽ có lỗi cố ý (ví dụ một ống xoá kích
thước), bấm kiểm tra, danh sách hiện đúng lỗi đó.

### 2.2 Click lỗi để zoom tới ống

- Từ danh sách kiểm tra ở 2.1, click một dòng → viewport di chuyển và phóng
  to đến đúng đoạn ống/fitting đó, highlight nó.
- Đây là nền tảng UX cho mọi cảnh báo về sau (clash, cao độ). Làm đúng một
  lần, dùng lại mãi.

Điều kiện hoàn thành: bấm vào một dòng lỗi, màn hình nhảy tới và làm nổi bật
đúng đối tượng; bấm dòng khác thì nhảy tới đối tượng khác.

---

## 3. Một tháng tới

Mục tiêu tháng: NEVIS bắt đầu "biết" tuyến ống đang nằm ở tầng nào và sàn
tầng đó ra sao — bước nhỏ nhất để sau này kiểm tra va chạm thật.

Nguyên tắc: chỉ làm phần tầng/sàn mà bản thân nó đã hiển thị và dùng được
ngay, không xây nền cao độ rồi để đó.

### 3.1 Mô hình tầng tối thiểu (nhìn thấy được)

- Cho phép project khai báo danh sách tầng: tên/mã tầng và chiều cao tầng.
- Không giả định mọi tầng cùng chiều cao.
- Ngay khi khai báo xong phải có thứ gì đó hiển thị: ví dụ chọn tầng hiện
  hành và NEVIS cho biết tuyến đang thuộc tầng nào.

Điều kiện hoàn thành: tạo 3 tầng với chiều cao khác nhau, chọn tầng hiện
hành, giao diện phản ánh đúng tầng đang chọn và chiều cao của nó.

### 3.2 Cấu tạo sàn tối thiểu

- Mỗi tầng khai báo được: cao độ sàn (SL/FL theo quy ước dự án) và dày bê
  tông sàn.
- Không hard-code một ý nghĩa SL/FL duy nhất; cho dự án tự định nghĩa.
- Chưa cần sàn giật cấp, sàn nâng, trần — để các tuần sau.

Điều kiện hoàn thành: nhập SL, FL và dày sàn cho một tầng, mở lại project
thấy giá trị được lưu và hiển thị đúng.

### 3.3 Suy cao độ tuyến từ 集合管 + 1/N (thử nghiệm hiển thị)

- Chọn một anchor (集合管 hoặc điểm xuyên), chọn hướng dòng, áp 1/N.
- NEVIS hiển thị cao độ suy ra dọc tuyến (đọc, chưa ghi đè model).
- Người dùng KHÔNG nhập Z từng đoạn. Đây là điểm khác biệt cốt lõi so với
  hướng Elevation cũ.

Điều kiện hoàn thành: chọn 集合管, đặt 1/100, NEVIS hiển thị cao độ giảm dần
hợp lý dọc tuyến; đổi sang 1/50 thì độ dốc hiển thị thay đổi tương ứng.

---

## 4. Việc CHƯA làm (để sau, không phải bỏ)

Những việc này đúng hướng nhưng chưa tới lượt. Chưa làm cho đến khi mục 1–3
xong và ổn định:

- Kiểm tra va chạm thật (ống–sàn, ống–dầm, ống–ống) với envelope đầy đủ.
- Trần và khung trần.
- Sàn giật cấp, sàn nâng/sàn gỗ.
- Thiết bị và vùng bảo trì.
- Gợi ý xử lý tự động (nâng/hạ/đổi tuyến).
- PDF/Image recognition.
- AI route suggestion.
- Tách monolithic `Nevis_no_ui.py` thành nhiều file.

Lý do hoãn: tất cả đều cần mục 1–3 làm nền, và không cái nào tạo giá trị nhìn
thấy nếu làm trước.

---

## 5. Việc PHẢI DỪNG (đã dừng)

Theo Elevation Reality Reset, các hướng sau dừng lại, không phát triển tiếp:

- Apply Engine như milestone tiếp theo.
- Level Manager như workflow bắt buộc.
- Elevation Preview dạng bảng đề xuất cao độ.
- Nhập cao độ thủ công cho từng đoạn ống.
- Mở rộng pipeline chỉ để lan truyền giá trị Z.
- Phần trăm độ dốc làm input chính.

Phần hạ tầng cũ (graph topology, anchor discovery, highlight overlay, undo
transaction) giữ lại để tái sử dụng có chọn lọc, KHÔNG tiếp tục theo dạng
milestone B1→B6.

---

## 6. Kiểm tra mỗi ngày: có đi lạc không?

Cuối mỗi ngày làm việc, trả lời 5 câu. Nếu có một câu "không", ngày mai phải
sửa hướng trước khi làm tiếp.

1. **Nhìn thấy chưa?** Mở NEVIS có thấy việc hôm nay không? Nếu chỉ có code
   chạy ngầm, hôm nay đã đi lạc sang hạ tầng.
2. **Người dùng được lợi gì?** Nói được trong một câu: "việc này giúp nhanh
   hơn ở chỗ X" hoặc "chặn lỗi Y". Không nói được = đi lạc.
3. **Có phá cái đang đúng không?** Drainage, BOM, JWW export vẫn cho kết quả
   như cũ? Nếu chưa kiểm, chưa được coi là xong.
4. **Có bắt người dùng nhập thừa không?** Đặc biệt: có đang bắt nhập Z từng
   đoạn không? Nếu có, đó là tái phạm sai lầm Elevation.
5. **Điều kiện hoàn thành còn rõ không?** Bước đang làm vẫn có câu "mở NEVIS,
   làm X, thấy Y" chứ? Nếu điều kiện đã mờ đi, dừng và viết lại trước khi code.

Kiểm tra mỗi tuần một lần: dạng nhập/hiển thị độ dốc còn là `1/N` không, ngôn
ngữ UI còn đúng không, và danh sách "việc phải dừng" có món nào lén quay lại
không.

---

## 7. Thứ tự ưu tiên hiện tại (chốt)

1. Sửa lỗi ngôn ngữ UI.
2. Độ dốc dạng 1/N.
3. Kiểm tra dữ liệu ống nhanh.
4. Click lỗi để zoom tới ống.
5. Mô hình tầng/sàn tối thiểu.

Không đảo thứ tự để chạy theo tính năng "kêu" hơn. Mỗi món xong và ổn định
mới sang món sau. Một kết quả đúng và dùng được hôm nay quan trọng hơn một
nền tảng to chưa ai bấm được.
