# Elevation Reality Reset

Date: 2026-06-18
Status: Product-direction reset

## Tuyên bố định hướng

NEVIS là phần mềm ứng dụng cho thiết kế triển khai và thi công thực tế.

Mục tiêu chính không phải xây dựng một hệ thống nhập, truyền và áp dụng cao độ
mang tính học thuật. Mục tiêu là giúp người dùng nhìn nhanh thấy đường ống có
va chạm với môi trường công trình hay không, va chạm ở đâu, chạm đối tượng nào
và nên xử lý thế nào.

Tạm dừng phát triển tiếp các hướng sau:

- Level Manager.
- Apply Engine.
- Elevation Preview theo dạng bảng đề xuất cao độ.
- Nhập cao độ thủ công cho từng đoạn ống.
- Mở rộng pipeline chỉ để lan truyền giá trị Z.

Các tài liệu và module hiện có được xem là lịch sử kỹ thuật hoặc hạ tầng có thể
tái sử dụng. Chúng không còn quyết định mục tiêu sản phẩm tiếp theo.

## 1. Hướng hiện tại sai ở đâu

### Lấy dữ liệu cao độ làm mục tiêu thay vì phương tiện

Hướng hiện tại tập trung vào:

- Tìm anchor cao độ.
- Truyền Z qua topology.
- Phân loại proposed/conflict/locked/skipped.
- Ghi `edge.start_z` và `edge.end_z`.
- Xây UI để xem và áp dụng các giá trị đó.

Những việc này trả lời câu hỏi "cao độ nào sẽ được ghi vào model", nhưng chưa
trả lời câu hỏi quan trọng của người thi công:

- Ống có chạm ống khác không?
- Ống có chạm sàn hoặc dầm không?
- Ống có đi vào vùng trần hoặc khung trần không?
- Ống có vướng máy móc, thiết bị hoặc không gian bảo trì không?
- Vị trí cụ thể cần sửa nằm ở đâu?

### Model hiện tại chưa đại diện cho vật thể thi công

Một đường tim có Z chưa đủ để kiểm tra va chạm. Kiểm tra thực tế cần biết:

- Đường kính ngoài của ống.
- Lớp bảo ôn hoặc lớp bọc nếu có.
- Không gian lắp đặt và dung sai thi công.
- Cao độ tham chiếu là đáy ống, tim ống hay đỉnh ống.
- Bề dày và vùng chiếm chỗ của sàn, dầm, trần, khung trần, thiết bị.
- Lỗ mở, sleeve, shaft hoặc vùng xuyên được phép.

Nếu chỉ so sánh Z của đường tim, hệ thống có thể báo thiếu va chạm hoặc báo sai
va chạm.

### Bắt người dùng nhập quá nhiều dữ liệu cục bộ

Nhập cao độ cho từng đoạn ống làm tăng thao tác và dễ tạo dữ liệu mâu thuẫn.
Trong nhiều công trình, phần lớn cao độ có thể suy ra từ:

- Vị trí và cao độ của `集合管`.
- Tầng chứa tuyến ống.
- Chiều cao tầng và cấu tạo sàn.
- Hướng thoát nước.
- Độ dốc `1/N`.
- Chiều dài tuyến và topology đã có trên bản vẽ.

Nhập từng đoạn chỉ nên là ngoại lệ để xử lý trường hợp đặc biệt, không phải
workflow chính.

### Dùng phần trăm độ dốc làm trung tâm không phù hợp thói quen thực tế

Trong triển khai thoát nước, người dùng thường làm việc với dạng `1/N` như:

- `1/50`.
- `1/75`.
- `1/100`.

Phần trăm có thể tồn tại như giá trị quy đổi nội bộ hoặc thông tin phụ, nhưng
không nên là cách nhập và hiển thị chính.

### Output hiện tại chưa đủ hành động

Một dòng "conflict" hoặc "proposed Z" không đủ để sửa bản vẽ. Người dùng cần:

- Điểm va chạm được highlight trực tiếp.
- Tên hoặc loại đối tượng bị chạm.
- Khoảng thiếu clearance.
- Mức độ nghiêm trọng.
- Gợi ý nâng, hạ, đổi tuyến, đổi độ dốc hoặc tạo lỗ mở.

## 2. Mục tiêu thực tế mới

Xây dựng khả năng kiểm tra va chạm phục vụ thi công từ bản vẽ ống thực tế.

Hệ thống cần dựng được một mô hình không gian vừa đủ từ dữ liệu công trình và
tuyến ống, sau đó kiểm tra:

1. Ống với ống.
2. Ống với sàn và các lớp cấu tạo sàn.
3. Ống với kết cấu như dầm, cột, tường hoặc vùng kết cấu cấm đi xuyên.
4. Ống với trần và khung trần.
5. Ống với máy móc, thiết bị và vùng bảo trì cần tránh.
6. Ống với giới hạn không gian lắp đặt hoặc clearance quy định.

Kết quả phải ưu tiên trực quan:

- Nhìn thấy lỗi trên bản vẽ.
- Chọn lỗi để đi ngay tới vị trí.
- Hiểu nguyên nhân mà không cần đọc dữ liệu kỹ thuật dài.
- Có gợi ý xử lý thực tế.

## 3. Input thực tế cần có

### 3.1 Thông tin tầng

- Số tầng của công trình.
- Tên hoặc mã tầng.
- Chiều cao từng tầng.
- Cao độ gốc công trình.
- Quan hệ giữa các tầng nếu chiều cao không đồng nhất.

Không giả định mọi tầng có cùng chiều cao.

### 3.2 SL/FL theo từng công trình

NEVIS cần cho phép dự án định nghĩa rõ:

- `SL`: Structural Level hoặc định nghĩa tương đương của dự án.
- `FL`: Finished Level hoặc định nghĩa tương đương của dự án.
- Quan hệ giữa SL và FL.
- Level nào được dùng làm mốc cho từng loại kiểm tra.

Không hard-code một ý nghĩa duy nhất nếu hồ sơ công trình dùng quy ước khác.

### 3.3 Sàn bê tông

- Cao độ mặt trên/mặt dưới sàn.
- Dày sàn bê tông.
- Vùng biên hình học của sàn.
- Lỗ mở, shaft, sleeve và vùng xuyên được phép.
- Khu vực có chiều dày khác tiêu chuẩn.

### 3.4 Sàn giật cấp

- Vùng polygon hoặc vùng mặt bằng bị giật cấp.
- Độ chênh cao.
- Cao độ mặt trên và mặt dưới tại từng vùng.
- Mép chuyển cấp cần cảnh báo nếu tuyến ống đi qua.

### 3.5 Sàn gỗ hoặc nâng sàn

- Chiều cao lớp sàn hoàn thiện.
- Khoang rỗng dưới sàn.
- Khung đỡ hoặc chân đỡ nếu cần tránh.
- Vùng được phép đi ống và vùng bị cấm.

### 3.6 Trần và khung trần

- Cao độ trần hoàn thiện.
- Chiều cao khoang trần.
- Cao độ và vùng chiếm chỗ của khung trần.
- Vùng trần giật cấp.
- Không gian dành cho đèn, miệng gió, sprinkler hoặc thiết bị trần.

### 3.7 Cấu kiện và thiết bị cần tránh

Tối thiểu cần mô tả được:

- Dầm.
- Cột.
- Tường hoặc vách.
- Móng/bệ thiết bị nếu nằm trong phạm vi tuyến.
- Máy móc và thiết bị MEP.
- Vùng thao tác, mở cửa, tháo lắp và bảo trì.
- Vùng cấm đi ống do yêu cầu công nghệ hoặc thi công.

Hình học ban đầu có thể là box, polygon extrusion hoặc vùng clearance đơn giản;
không cần bắt đầu bằng mô hình BIM đầy đủ.

### 3.8 Độ dốc dạng `1/N`

Input chính:

- Giá trị `N`.
- Hướng dốc.
- Điểm hoặc thiết bị làm mốc.
- Quy tắc đổi dốc theo loại và kích thước ống nếu có.

Phần trăm chỉ là giá trị quy đổi:

```text
slope_percent = 100 / N
```

UI và báo cáo chính phải ưu tiên hiển thị `1/N`.

### 3.9 Dữ liệu ống thực tế

Ngoài danh sách bắt buộc trên, collision check cần tối thiểu:

- Tâm tuyến trên mặt bằng.
- Kích thước/đường kính ngoài.
- Vật liệu hoặc loại ống khi ảnh hưởng kích thước ngoài.
- Bảo ôn/lớp bọc.
- Clearance thi công.
- Loại hệ thống.
- Cao độ tham chiếu: đáy, tim hoặc đỉnh ống.
- Điểm neo thực tế như `集合管`, thiết bị đầu/cuối hoặc điểm xuyên sàn.

Các giá trị đã có trong thư viện vật tư phải được tái sử dụng, không yêu cầu
người dùng nhập lại.

## 4. Cách suy ra tuyến cao độ mà không nhập từng đoạn

Workflow ưu tiên:

1. Xác định tầng và cấu tạo sàn của tuyến.
2. Xác định anchor đáng tin cậy, ưu tiên `集合管`, thiết bị hoặc điểm xuyên.
3. Xác định hướng dòng chảy.
4. Áp dụng độ dốc `1/N` dọc theo chiều dài thực của tuyến.
5. Truyền profile qua các đoạn liên tục theo topology.
6. Dừng và yêu cầu xác nhận tại nhánh, vòng, nhiều anchor mâu thuẫn hoặc vùng
   chuyển tầng/cấu tạo.
7. Chỉ cho phép manual override tại điểm đặc biệt.

Thứ tự ưu tiên dữ liệu đề xuất:

1. Anchor thi công rõ ràng.
2. Tầng và cấu tạo sàn.
3. Hướng dòng chảy.
4. Độ dốc `1/N`.
5. Topology và chiều dài tuyến.
6. Manual exception.

Manual exception phải được highlight và giải thích để tránh biến toàn bộ model
thành dữ liệu nhập tay.

## 5. Mô hình kiểm tra va chạm tối thiểu

### Pipe envelope

Mỗi đoạn ống cần được chuyển từ đường tim thành một envelope không gian gồm:

- Bán kính ngoài.
- Bảo ôn/lớp bọc.
- Clearance yêu cầu.
- Profile cao độ theo chiều dài.

Không dùng một Z duy nhất nếu đoạn ống có độ dốc.

### Obstacle envelope

Mỗi sàn, dầm, trần, khung hoặc thiết bị cần có vùng chiếm chỗ và clearance.

Giai đoạn đầu có thể dùng:

- 2.5D polygon + khoảng Z.
- Bounding box.
- Extruded profile.

Chỉ chuyển sang mesh/solid phức tạp khi dữ liệu và nhu cầu thực tế yêu cầu.

### Quy tắc tiếp xúc

Cần phân biệt:

- Va chạm thật.
- Thiếu clearance nhưng chưa giao hình học.
- Đi xuyên hợp lệ qua lỗ mở/sleeve.
- Đi xuyên sàn chưa có lỗ mở.
- Hai tuyến giao nhau trên mặt bằng nhưng khác cao độ và không chạm.
- Hai tuyến gần nhau nhưng vẫn đủ khoảng thi công.

Tolerance phải có giá trị mặc định thực tế và có thể cấu hình theo dự án.

## 6. Output cần có

### 6.1 Cảnh báo va chạm

Mỗi cảnh báo cần có:

- Loại va chạm.
- Mức độ: nghiêm trọng, cần kiểm tra, hoặc thiếu clearance.
- Trạng thái chưa xử lý/đã xác nhận/được phép.

### 6.2 Vị trí va chạm

Phải xác định được:

- Tầng.
- Tọa độ mặt bằng.
- Cao độ tại điểm va chạm.
- Đoạn ống và khoảng cách dọc đoạn/tuyến.
- Vùng va chạm hoặc đoạn giao nhau, không chỉ một row chung chung.

Khi chọn cảnh báo, NEVIS phải highlight và đưa viewport đến đúng vị trí.

### 6.3 Đối tượng bị chạm

Ví dụ:

- Ống khác.
- Mặt dưới sàn bê tông.
- Mép sàn giật cấp.
- Dầm.
- Cột/tường.
- Trần hoàn thiện.
- Khung trần.
- Thiết bị hoặc vùng bảo trì.

Tên hiển thị phải dùng thuật ngữ JP/VN qua language system của NEVIS.

### 6.4 Thông tin định lượng

Khi có thể, báo rõ:

- Độ xuyên chồng lấn.
- Khoảng clearance hiện tại.
- Khoảng clearance yêu cầu.
- Khoảng thiếu.
- Cao độ ống tại điểm kiểm tra.

### 6.5 Gợi ý xử lý

Gợi ý có thể gồm:

- Nâng hoặc hạ tuyến trong giới hạn cho phép.
- Đổi hướng đi ống.
- Đổi thứ tự trên/dưới giữa hai tuyến.
- Điều chỉnh `1/N` trong phạm vi tiêu chuẩn.
- Di chuyển điểm neo hoặc vị trí `集合管` nếu được phép.
- Tạo hoặc điều chỉnh lỗ mở/sleeve.
- Xác nhận vùng xuyên được phép.
- Yêu cầu phối hợp với kết cấu, trần hoặc thiết bị.

Gợi ý không được tự động sửa model trong giai đoạn cảnh báo đầu tiên.

## 7. UX ưu tiên thực tế

Workflow mục tiêu:

1. Người dùng chọn hoặc mở bản vẽ.
2. Chọn tầng/cấu tạo áp dụng.
3. Chọn anchor như `集合管` nếu hệ thống chưa nhận ra.
4. Nhập độ dốc `1/N` hoặc dùng mặc định theo rule.
5. Bấm kiểm tra va chạm.
6. Xem danh sách lỗi có màu và mức độ.
7. Chọn lỗi để highlight ngay trên bản vẽ.
8. Xem đối tượng bị chạm, khoảng thiếu và gợi ý xử lý.

Nguyên tắc UX:

- Ít trường nhập nhất có thể.
- Không bắt nhập Z từng đoạn.
- Không yêu cầu hiểu pipeline nội bộ.
- Cảnh báo phải ngắn, rõ và có vị trí.
- Mặc định phải phù hợp công việc thoát nước thực tế.
- Cho phép override nhưng không biến override thành workflow chính.

## 8. Phần hạ tầng cũ có thể tái sử dụng

Không phải toàn bộ công việc cũ đều bỏ đi. Có thể tái sử dụng có chọn lọc:

- Graph topology của tuyến ống.
- Anchor discovery sau khi định nghĩa lại anchor thi công.
- Endpoint-pair identity.
- Conflict/lock reporting pattern.
- Read-only result architecture.
- Highlight overlay concept.
- Undo Transaction cho các thao tác sửa thật trong tương lai.

Không nên tái sử dụng nguyên trạng:

- Giả định endpoint Z là sản phẩm chính.
- Apply Engine như milestone tiếp theo.
- Level Manager như workflow bắt buộc.
- Preview chỉ hiển thị proposed Z.
- Phần trăm độ dốc làm input chính.

## 9. Hướng tài liệu tiếp theo

Trước khi code mới, cần tài liệu yêu cầu thực tế riêng cho collision checking:

1. Danh mục loại va chạm ưu tiên.
2. Quy ước tầng, SL/FL và cấu tạo sàn.
3. Pipe/obstacle envelope tối thiểu.
4. Quy tắc suy cao độ từ `集合管` và `1/N`.
5. Format cảnh báo và highlight.
6. Bộ case công trình mẫu để kiểm chứng.

Không tiếp tục Apply/UI cũ trước khi các yêu cầu này được duyệt.

## 10. Điều kiện thành công

Hướng mới chỉ được coi là đúng khi NEVIS có thể, với thao tác tối thiểu:

- Suy ra profile cao độ hợp lý của tuyến.
- Phát hiện đúng va chạm quan trọng.
- Không báo va chạm giả khi hai ống chỉ giao nhau trên mặt bằng.
- Chỉ đúng vị trí lỗi.
- Nói rõ đối tượng bị chạm.
- Đưa ra gợi ý xử lý có ích cho thi công.
- Không bắt người dùng nhập cao độ cho từng đoạn ống.
- Dùng `1/N` làm ngôn ngữ độ dốc chính.

Tiêu chí cuối cùng không phải số lượng module hay số dòng dữ liệu cao độ được
ghi. Tiêu chí là người dùng nhìn thấy lỗi nhanh hơn, hiểu lỗi rõ hơn và sửa bản
vẽ thực tế dễ hơn.
