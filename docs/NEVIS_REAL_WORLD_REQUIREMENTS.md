# NEVIS Real-World Requirements

Date: 2026-06-18
Status: Product requirements - no technical design

## 1. Mục đích

Tài liệu này tổng hợp bài toán thực tế NEVIS cần giải quyết cho công việc triển
khai MEP và thi công tại Nhật Bản.

NEVIS phải giúp người dùng:

- Đọc và tận dụng bản vẽ hiện có nhanh hơn.
- Giảm thao tác vẽ, đo bóc và kiểm tra lặp lại.
- Phát hiện lỗi trước khi phát hành bản vẽ hoặc thi công.
- Nhìn thấy rõ lỗi nằm ở đâu, liên quan đến đối tượng nào và cần kiểm tra gì.
- Tạo đầu ra phù hợp với cách làm việc thực tế bằng JWW, CAD và PDF.

NEVIS không được coi việc hoàn thiện dữ liệu cao độ là mục tiêu tự thân. Cao độ,
vật liệu và thông tin không gian chỉ có giá trị khi giúp tạo bản vẽ đúng, bóc
tách đúng, phát hiện va chạm hoặc giảm thời gian xử lý.

## 2. Quy ước ưu tiên

- **P1 - Phải có:** thiếu yêu cầu này thì NEVIS chưa giải quyết được công việc
  cốt lõi hoặc vẫn để lại rủi ro thi công lớn.
- **P2 - Nên có:** tạo giá trị rõ ràng và giảm nhiều thao tác, nhưng công việc
  chính vẫn có thể thực hiện bằng kiểm tra hoặc bổ sung thủ công.
- **P3 - Tương lai:** có tiềm năng lớn nhưng chỉ nên làm sau khi các yêu cầu P1
  ổn định và được xác nhận bằng dự án thực tế.

## A. Giá trị cốt lõi hiện tại

### A1. JWW integration - P1

NEVIS phải làm việc tốt với JWW vì đây là đầu vào và đầu ra chính trong nhiều
quy trình triển khai tại Nhật.

Yêu cầu thực tế:

- Nhận dữ liệu bản vẽ từ JWW mà không bắt người dùng dựng lại từ đầu.
- Giữ đúng tỷ lệ, tọa độ, hướng, kích thước và quan hệ hình học quan trọng.
- Xuất kết quả để tiếp tục chỉnh sửa và phát hành trong JWW.
- Giữ nét, ký hiệu, layer và cách thể hiện đủ gần tiêu chuẩn bản vẽ đang dùng.
- Hạn chế tối đa việc sửa tay sau khi xuất.
- Khi không nhận diện chắc chắn, phải cho người dùng biết phần nào cần kiểm tra.

### A2. CAD/PDF recognition - P1

NEVIS phải tận dụng được bản vẽ kiến trúc, kết cấu và MEP có sẵn dưới dạng CAD
hoặc PDF.

Yêu cầu thực tế:

- Nhận biết các đường, ký hiệu, chữ và kích thước cần thiết cho công việc.
- Phân biệt được thông tin chắc chắn với thông tin chỉ là dự đoán.
- Cho phép người dùng xác nhận hoặc sửa nhanh kết quả nhận diện.
- Không yêu cầu người dùng vẽ lại toàn bộ mặt bằng chỉ để bắt đầu kiểm tra.
- Hỗ trợ bản vẽ không hoàn hảo: layer lộn xộn, scan, nét đứt hoặc chất lượng PDF
  không đồng đều.
- Ghi nhớ phần đã xác nhận để tránh làm lại trong cùng dự án.

### A3. Material takeoff - P1

NEVIS phải bóc tách được khối lượng phục vụ đặt hàng, chuẩn bị vật tư và kiểm tra
thiếu sót.

Yêu cầu thực tế:

- Tổng hợp chiều dài ống theo hệ, vật liệu và kích thước.
- Đếm fitting, phụ kiện, thiết bị và các chi tiết cần thiết.
- Phân biệt vật liệu thường, vật liệu chống cháy và các trường hợp đặc biệt.
- Tránh đếm trùng tại điểm nối, reducer, fitting tổ hợp hoặc vùng chuyển vật liệu.
- Cho phép truy ngược một dòng khối lượng về vị trí trên bản vẽ.
- Nêu rõ đối tượng thiếu thông tin nên chưa thể bóc chính xác.
- Xuất báo cáo dễ kiểm tra và dùng tiếp trong công việc thực tế.

### A4. Section generation - P1

NEVIS phải giúp tạo mặt cắt tại vị trí cần kiểm tra hoặc trình bày mà không bắt
người dùng dựng lại thủ công.

Yêu cầu thực tế:

- Tạo mặt cắt từ tuyến và phạm vi người dùng chọn.
- Thể hiện được ống, kích thước, cao độ và các vật thể công trình liên quan.
- Làm rõ quan hệ trên/dưới và khoảng hở tại vùng quan trọng.
- Cho phép người dùng chọn hướng nhìn và phạm vi mặt cắt.
- Kết quả phải đủ rõ để kiểm tra, trao đổi và đưa vào bản vẽ thi công.
- Cảnh báo khi dữ liệu đầu vào chưa đủ để mặt cắt đáng tin cậy.

### A5. Clash detection - P1

NEVIS phải phát hiện các xung đột có khả năng gây sửa bản vẽ, sửa tại công
trường hoặc không thể lắp đặt.

Yêu cầu thực tế:

- Kiểm tra ống với ống và với các vật thể công trình quan trọng.
- Phân biệt va chạm thật, thiếu khoảng hở và trường hợp chưa đủ dữ liệu.
- Chỉ đúng vị trí lỗi trên bản vẽ, không chỉ đưa một danh sách chung chung.
- Cho biết các đối tượng liên quan và mức độ ảnh hưởng.
- Hạn chế cảnh báo giả để người dùng không bỏ qua toàn bộ kết quả.
- Cho phép đánh dấu đã kiểm tra, được chấp nhận hoặc cần xử lý.

### A6. Japanese MEP rules - P1

NEVIS phải phù hợp với cách thể hiện, vật tư và quy tắc MEP đang dùng trong dự
án Nhật Bản.

Yêu cầu thực tế:

- Dùng đúng tên gọi, ký hiệu và cách ghi kích thước quen thuộc.
- Hỗ trợ các loại ống, fitting và vật liệu thực tế của dự án.
- Kiểm tra các yêu cầu về độ dốc, khoảng hở, xuyên kết cấu, chống cháy và bảo trì
  theo rule được dự án áp dụng.
- Phân biệt quy định bắt buộc, tiêu chuẩn công ty và quy ước riêng của dự án.
- Không áp một rule chung cho mọi dự án khi điều kiện thực tế khác nhau.
- Kết quả kiểm tra phải giải thích được rule nào tạo ra cảnh báo.
- Giao diện và báo cáo cần dùng được bằng tiếng Nhật và tiếng Việt.

## B. Dữ liệu công trình tối thiểu cần có

Mục tiêu của dữ liệu công trình là đủ để nhìn thấy không gian thi công và kiểm
tra tuyến. Không yêu cầu người dùng dựng một mô hình công trình đầy đủ hơn nhu
cầu thực tế.

### B1. Tầng - P1

Cần biết:

- Tên hoặc mã tầng.
- Phạm vi tầng áp dụng cho bản vẽ.
- Cao độ tham chiếu cần thiết.
- Quan hệ với tầng trên và tầng dưới khi có tuyến xuyên tầng.
- Khu vực có cao độ khác với phần còn lại của tầng.

### B2. Sàn - P1

Cần biết:

- Phạm vi sàn.
- Mặt trên, mặt dưới hoặc chiều dày cần cho kiểm tra.
- Vùng có lỗ mở, sleeve hoặc shaft.
- Vùng không được phép xuyên.
- Sự khác nhau giữa sàn kết cấu và mặt sàn hoàn thiện khi có ảnh hưởng.

### B3. Sàn giật cấp - P1

Cần biết:

- Phạm vi vùng giật cấp.
- Mức chênh cao so với khu vực xung quanh.
- Vị trí mép chuyển cấp.
- Chiều dày hoặc mặt dưới liên quan đến không gian đi ống.
- Lỗ mở và vùng được phép xuyên trong khu vực đó.

### B4. Dầm - P1

Cần biết:

- Vị trí và phạm vi chiếm chỗ.
- Chiều rộng, chiều cao và cao độ đáy dầm.
- Dầm kết cấu nào không được phép xuyên.
- Vị trí lỗ xuyên đã được chấp thuận nếu có.
- Khu vực cần giữ khoảng cách thi công.

### B5. Cột - P1

Cần biết:

- Vị trí và kích thước mặt bằng.
- Phạm vi theo chiều cao.
- Khu vực không được đi ống hoặc cần giữ khoảng cách.
- Sự thay đổi kích thước/vị trí giữa các tầng nếu có.

### B6. Tường - P1

Cần biết:

- Vị trí, chiều dày và chiều cao.
- Tường kết cấu, tường chống cháy hoặc tường có yêu cầu đặc biệt.
- Cửa, lỗ mở, sleeve và vị trí xuyên được phép.
- Khu vực cấm xuyên hoặc cần phối hợp trước.

### B7. Vách - P2

Cần biết:

- Vị trí, chiều dày và chiều cao.
- Loại vách khi ảnh hưởng đến cách xuyên hoặc hoàn thiện.
- Yêu cầu chống cháy/cách âm nếu dự án cung cấp.
- Lỗ mở và điều kiện phục hồi sau khi xuyên.

Vách thường dễ điều chỉnh hơn tường kết cấu, nhưng không được mặc định rằng mọi
vách đều có thể xuyên tự do.

### B8. Trần - P1

Cần biết:

- Cao độ mặt trần hoàn thiện.
- Phạm vi và vùng trần giật cấp.
- Không gian phía trên trần dành cho MEP.
- Khu vực có khung trần, đèn, miệng gió, sprinkler hoặc thiết bị khác.
- Lỗ thăm và vùng cần tiếp cận để bảo trì.

### B9. Thiết bị - P1

Cần biết:

- Vị trí, kích thước và phạm vi chiếm chỗ.
- Điểm kết nối ống.
- Hướng lắp đặt và tháo lắp.
- Khoảng trống cần cho vận hành, mở cửa và bảo trì.
- Vùng không được đặt ống vì ảnh hưởng thao tác hoặc an toàn.
- Thiết bị cố định và thiết bị còn có thể điều chỉnh vị trí.

### B10. Dữ liệu bổ sung có giá trị - P2

- Shaft và vùng kỹ thuật.
- Cửa và vùng mở cửa.
- Hộp kỹ thuật, access panel và lỗ thăm.
- Máng cáp, ống gió và các hệ MEP khác.
- Vùng dành riêng cho từng bộ môn.
- Vùng cấm do vận hành, an toàn hoặc yêu cầu của khách hàng.

## C. Các lỗi thi công cần phát hiện

### C1. Va chạm vật lý - P1

- Ống chạm hoặc xuyên ống khác.
- Ống chạm dầm, cột, sàn, tường hoặc vách.
- Ống chạm trần, khung trần hoặc thiết bị.
- Fitting lắp được trên đường tim nhưng thân fitting va chạm vật thể khác.
- Bảo ôn hoặc lớp bảo vệ va chạm dù thân ống chưa chạm.
- Hai đối tượng không chạm trên mặt bằng nhưng va chạm do cao độ thực tế.

### C2. Xuyên kết cấu không hợp lệ - P1

- Ống xuyên sàn/tường ngoài opening hoặc sleeve đã cho phép.
- Ống đi lệch, quá lớn hoặc quá sát mép opening.
- Ống xuyên dầm/cột khi chưa có chấp thuận.
- Nhiều ống dùng chung opening nhưng tổng không gian không đủ.
- Vị trí xuyên xung đột với thép, chống cháy hoặc yêu cầu kết cấu đã biết.

### C3. Thiếu khoảng hở - P1

- Không đủ khoảng hở giữa hai ống.
- Không đủ khoảng hở tới sàn, dầm, tường, trần hoặc thiết bị.
- Không đủ chỗ cho bảo ôn, kẹp, ty treo hoặc thao tác nối ống.
- Không đủ khoảng trống để lắp fitting thực tế.
- Không đủ vùng tiếp cận để kiểm tra, vệ sinh, sửa chữa hoặc thay thiết bị.

### C4. Lỗi cao độ và độ dốc - P1

- Độ dốc sai hướng hoặc không đủ theo yêu cầu dự án.
- Cao độ đầu/cuối không phù hợp với điểm kết nối.
- Tuyến bị mất độ dốc tại nhánh, fitting hoặc đoạn chuyển hướng.
- Ống tụt dưới trần hoặc đi vào vùng sử dụng nhìn thấy được.
- Ống nâng quá cao và chạm sàn/dầm phía trên.
- Tuyến xuyên tầng không khớp vị trí hoặc cao độ liên quan.

### C5. Lỗi kết nối và tính liên tục - P1

- Đầu ống hở, nối thiếu hoặc nối nhầm tuyến.
- Kích thước hai đầu không phù hợp nhưng thiếu reducer đúng.
- Fitting không phù hợp hướng, kích thước hoặc loại ống.
- Tuyến bị trùng, đứt hoặc chồng đoạn ngoài ý muốn.
- Điểm kết nối thiết bị không khớp tuyến.
- Hướng dòng chảy hoặc quan hệ nhánh không hợp lý.

### C6. Lỗi vật liệu và quy cách - P1

- Vật liệu không phù hợp hệ thống hoặc khu vực sử dụng.
- Thiếu chuyển vật liệu/chống cháy tại ranh giới yêu cầu.
- Kích thước ống hoặc fitting không thống nhất.
- Dùng phụ kiện không có trong quy cách dự án.
- Bóc tách thiếu vật tư do đối tượng chưa xác định hoặc bị đếm sai.

### C7. Lỗi phối hợp bản vẽ - P2

- Mặt bằng, mặt cắt và chi tiết thể hiện không thống nhất.
- Cao độ/kích thước ghi chú khác dữ liệu tuyến.
- Bản vẽ kiến trúc/kết cấu đã thay đổi nhưng tuyến chưa cập nhật.
- Cùng một vị trí có nhiều thông tin mâu thuẫn.
- Ký hiệu, tên gọi hoặc layer gây hiểu nhầm khi giao bản vẽ.

### C8. Lỗi khả năng thi công và bảo trì - P2

- Có không gian hình học nhưng không đủ đường đưa ống/fitting vào lắp.
- Không thể thao tác nối, siết, hàn hoặc kiểm tra tại vị trí dự kiến.
- Van, cửa thăm hoặc thiết bị bị che khuất.
- Không thể tháo thiết bị hoặc thay phụ kiện sau khi hoàn thiện.
- Thứ tự lắp đặt giữa các hệ gây khóa đường thi công.
- Tuyến đúng bản vẽ nhưng không phù hợp dung sai công trường.

## D. Các tính năng tiết kiệm thời gian nhất

### D1. Nhận bản vẽ và dựng tuyến nhanh - P1

- Tận dụng trực tiếp JWW/CAD/PDF hiện có.
- Nhận diện đường ống, kích thước, ký hiệu và fitting phổ biến.
- Cho phép xác nhận/sửa hàng loạt thay vì sửa từng đối tượng.
- Tái sử dụng thư viện và quy tắc đã xác nhận của dự án.

### D2. Tạo bản vẽ đầu ra ít phải sửa tay - P1

- Xuất JWW đúng cách thể hiện đã thống nhất.
- Tạo ký hiệu, kích thước và ghi chú nhất quán.
- Tạo mặt cắt tại vị trí người dùng cần kiểm tra.
- Cập nhật đầu ra khi tuyến thay đổi mà không làm lại toàn bộ.

### D3. Bóc tách vật tư tự động và có thể kiểm tra - P1

- Cập nhật khối lượng từ trạng thái bản vẽ hiện tại.
- Nhóm theo hệ, vật liệu, kích thước và khu vực/tầng.
- Chỉ ra nguồn của từng số lượng.
- Cảnh báo phần chưa thể tính thay vì âm thầm bỏ qua.

### D4. Kiểm tra lỗi theo một thao tác - P1

- Chạy các kiểm tra quan trọng cho tầng, vùng hoặc tuyến được chọn.
- Sắp xếp lỗi theo mức độ ảnh hưởng thực tế.
- Chọn lỗi để đi thẳng tới đúng vị trí trên bản vẽ.
- Không bắt người dùng đọc bảng dữ liệu dài để hiểu vấn đề.
- Giữ trạng thái đã kiểm tra và lý do chấp nhận ngoại lệ.

### D5. So sánh thay đổi bản vẽ - P2

- Cho biết kiến trúc/kết cấu/MEP đã thay đổi ở đâu.
- Chỉ ra tuyến, mặt cắt và khối lượng bị ảnh hưởng.
- Tránh kiểm tra lại toàn bộ dự án khi chỉ một vùng thay đổi.
- Phân biệt thay đổi thật với khác biệt trình bày không quan trọng.

### D6. Gợi ý xử lý có kiểm soát - P2

- Gợi ý nâng/hạ, đổi hướng, đổi thứ tự trên/dưới hoặc điều chỉnh vị trí.
- Nêu rõ lỗi nào được giải quyết và ràng buộc nào có thể bị ảnh hưởng.
- Cho người dùng quyết định; không tự sửa hàng loạt mà không xác nhận.
- Không đề xuất phương án trái rule dự án hoặc làm mất khả năng bảo trì.

### D7. Tái sử dụng kiến thức dự án - P2

- Ghi nhớ vật liệu, ký hiệu và quy ước đã xác nhận.
- Dùng lại mẫu tầng, khu vực và chi tiết thường gặp.
- Dùng lại quyết định đã được phê duyệt cho trường hợp tương tự.
- Tránh bắt người dùng nhập lại cùng một thông tin nhiều lần.

### D8. Tự động tối ưu tuyến - P3

- Đề xuất nhiều phương án tuyến theo không gian thực tế.
- So sánh phương án theo va chạm, vật tư, chiều dài và khả năng thi công.
- Hỗ trợ lựa chọn phương án nhưng không thay quyết định của kỹ sư/người triển
  khai.

## E. Bảng ưu tiên tổng hợp

### E1. P1 - Phải có

- JWW integration dùng được trong quy trình thực tế.
- Nhận diện CAD/PDF với bước xác nhận rõ ràng.
- Material takeoff chính xác và truy ngược được.
- Section generation phục vụ kiểm tra và bản vẽ thi công.
- Clash detection có vị trí, đối tượng và mức độ rõ ràng.
- Japanese MEP rules theo rule của dự án.
- Dữ liệu tối thiểu về tầng, sàn, sàn giật cấp, dầm, cột, tường, trần và thiết
  bị.
- Phát hiện va chạm vật lý, xuyên kết cấu sai và thiếu khoảng hở.
- Phát hiện lỗi cao độ, độ dốc, kết nối, vật liệu và quy cách.
- Nhập/dựng tuyến nhanh, xuất ít sửa tay, bóc tách tự động và kiểm tra lỗi theo
  một thao tác.
- Mọi kết luận phải phân biệt PASS, có lỗi và chưa đủ dữ liệu.

### E2. P2 - Nên có

- Dữ liệu chi tiết về vách, shaft, cửa, vùng kỹ thuật và các hệ MEP khác.
- Phát hiện lỗi phối hợp bản vẽ, khả năng thi công và bảo trì.
- So sánh thay đổi giữa các phiên bản bản vẽ.
- Gợi ý xử lý có kiểm soát.
- Tái sử dụng kiến thức, quyết định và quy ước của dự án.
- Quản lý trạng thái xử lý và ngoại lệ qua nhiều lần kiểm tra.

### E3. P3 - Tương lai

- Tự động đề xuất và so sánh nhiều phương án tuyến.
- Kiểm tra trình tự lắp đặt phức tạp giữa nhiều bộ môn.
- Dự đoán rủi ro từ dữ liệu lịch sử dự án.
- Tự động hóa sâu hơn sau khi các kiểm tra P1 đã đủ tin cậy trong dự án thật.

## 3. Tiêu chí xác nhận yêu cầu bằng dự án thực tế

Một yêu cầu chỉ được coi là có giá trị khi trả lời được ít nhất một câu hỏi:

- Có giảm thời gian dựng, sửa hoặc kiểm tra bản vẽ không?
- Có ngăn được lỗi phải sửa tại công trường không?
- Có làm khối lượng vật tư đáng tin cậy hơn không?
- Có giúp người dùng tìm và hiểu lỗi nhanh hơn không?
- Có phù hợp với dữ liệu đầu vào mà dự án thực sự cung cấp không?
- Có tạo đầu ra dùng được trong JWW/CAD/PDF mà không cần làm lại không?

Khi hai yêu cầu cạnh tranh, ưu tiên yêu cầu giải quyết lỗi thường gặp, hậu quả
lớn và có dữ liệu thực tế để kiểm tra. Không ưu tiên tính năng chỉ làm model chi
tiết hơn nhưng không cải thiện bản vẽ, khối lượng, kiểm tra hoặc thi công.

## 4. Ngoài phạm vi tài liệu

Tài liệu này không quyết định:

- Cấu trúc phần mềm.
- Module, class, schema hoặc API.
- Công nghệ nhận diện hoặc hình học.
- Cách lưu project.
- Cách triển khai collision/elevation.
- Kế hoạch code hoặc thứ tự commit.

Mọi thiết kế kỹ thuật chỉ được xem xét sau khi danh sách yêu cầu P1 được kiểm
chứng bằng bản vẽ và tình huống thi công thực tế.
