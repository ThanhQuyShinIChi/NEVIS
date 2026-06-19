# Construction Error Catalog

Date: 2026-06-18
Status: Real-world construction error requirements

## 1. Mục đích

Tài liệu này là danh mục các lỗi thi công đường ống mà NEVIS cần phát hiện trong
tương lai. Nội dung được nhìn từ ba công việc thực tế:

- Lập shopdrawing MEP.
- Phối hợp với kiến trúc, kết cấu và các bộ môn MEP khác.
- Kiểm tra bản vẽ trước khi phát hành cho công trường.

Mục tiêu không chỉ là tìm hai đường nét giao nhau. Một cảnh báo có giá trị phải
giúp người dùng nhận ra vị trí có thể gây khoan/cắt sai, không lắp được, phải
tháo làm lại, rò nước, mất độ dốc, ảnh hưởng hoàn thiện hoặc cản trở bảo trì.

## 2. Mức độ ưu tiên

- **P1 - Phải phát hiện:** nguy cơ ảnh hưởng kết cấu, chống thấm, an toàn, chức
  năng thoát nước hoặc gây phá dỡ/làm lại lớn.
- **P2 - Nên phát hiện:** thường gây sửa shopdrawing, đổi thứ tự thi công, thiếu
  không gian lắp đặt hoặc ảnh hưởng chất lượng hoàn thiện.
- **P3 - Kiểm tra bổ sung:** ít gây sự cố nghiêm trọng ngay lập tức nhưng làm
  giảm chất lượng, khả năng bảo trì hoặc hiệu quả thi công.

Mức ưu tiên có thể tăng theo loại công trình, khu vực chống cháy/chống thấm và
quy định riêng của dự án.

## A. Ống với kết cấu

### A1. Ống xuyên thân dầm ngoài vị trí được chấp thuận - P1

**Mô tả:** Thân ống, bảo ôn hoặc fitting đi vào phần chiếm chỗ của dầm nhưng
không nằm trong lỗ xuyên đã được kết cấu phê duyệt.

**Hậu quả:** Không thể thi công theo bản vẽ; có nguy cơ khoan/cắt thép, làm suy
giảm kết cấu, phải đổi tuyến gấp hoặc tháo phần đã lắp.

**Cách người dùng nhận biết:** Trên mặt bằng hoặc mặt cắt, tuyến cắt qua chiều
rộng và chiều cao dầm; tại vị trí đó không có sleeve/lỗ xuyên được chấp thuận.

### A2. Ống đi dưới dầm nhưng không đủ khoảng hở - P1

**Mô tả:** Ống không xuyên dầm nhưng đáy dầm và đỉnh ống, kể cả bảo ôn/kẹp treo,
không còn đủ khoảng lắp đặt.

**Hậu quả:** Ống bị hạ xuống dưới cao độ trần, không lắp được giá đỡ, hoặc phải
đổi cao độ của cả tuyến và các nhánh liên quan.

**Cách người dùng nhận biết:** Mặt cắt cho thấy envelope ống gần/chạm đáy dầm;
khoảng còn lại nhỏ hơn khoảng thi công yêu cầu của dự án.

### A3. Fitting hoặc mối nối nằm trong vùng dầm - P1

**Mô tả:** Đường tim đoạn thẳng có thể tránh dầm nhưng thân fitting, socket,
mối nối hoặc vùng thao tác lắp nối lại chạm dầm.

**Hậu quả:** Không thể lắp đúng phụ kiện, phải dịch fitting hoặc thay đổi bố trí
đoạn ống; dễ bị bỏ sót nếu chỉ kiểm tra đường tim.

**Cách người dùng nhận biết:** Khi xem chi tiết/mặt cắt, vị trí fitting nằm sát
mép hoặc bên trong dầm và không có đủ không gian thao tác quanh mối nối.

### A4. Ống xuyên sàn ngoài opening hoặc sleeve - P1

**Mô tả:** Tuyến đứng hoặc đoạn ống nghiêng xuyên qua sàn tại nơi chưa có lỗ mở,
sleeve hoặc vị trí xuyên được phê duyệt.

**Hậu quả:** Phải khoan cắt sau khi đổ bê tông, có nguy cơ chạm thép, hỏng chống
thấm/chống cháy và chậm tiến độ phối hợp với kết cấu.

**Cách người dùng nhận biết:** Vị trí ống giao mặt sàn nhưng không trùng với ký
hiệu hoặc danh sách lỗ chờ được chấp thuận.

### A5. Lỗ xuyên sàn không đủ cho ống và lớp hoàn thiện - P1

**Mô tả:** Có opening/sleeve nhưng kích thước hoặc hình dạng không đủ cho đường
kính ngoài, bảo ôn, dung sai lắp đặt và vật liệu trám hoàn thiện.

**Hậu quả:** Ống không luồn qua được, phải mở rộng lỗ, phá chống thấm hoặc không
đủ khe để xử lý chống cháy/chống nước đúng yêu cầu.

**Cách người dùng nhận biết:** Mép ngoài của ống/bảo ôn quá sát hoặc vượt khỏi
mép opening; khoảng trống xung quanh không đủ so với yêu cầu dự án.

### A6. Ống quá sát mép sàn hoặc mép opening - P1

**Mô tả:** Ống hoặc sleeve nằm gần mép sàn, mép ban công, mép hố hoặc mép lỗ mở
hơn giới hạn được kết cấu/kiến trúc cho phép.

**Hậu quả:** Khó cố định sleeve, có nguy cơ nứt vỡ mép bê tông, xung đột thép và
không đủ không gian chống thấm.

**Cách người dùng nhận biết:** Khoảng cách từ biên ống/sleeve tới mép cấu kiện
nhỏ hơn khoảng đã được dự án hoặc kết cấu xác nhận.

### A7. Ống va chạm cột - P1

**Mô tả:** Ống, fitting hoặc lớp bảo ôn đi vào phạm vi chiếm chỗ của cột.

**Hậu quả:** Không thể thi công; cột không phải đối tượng có thể khoan/cắt tùy
ý, nên thường phải đổi tuyến và ảnh hưởng nhiều nhánh.

**Cách người dùng nhận biết:** Trên mặt bằng, tuyến hoặc fitting giao footprint
cột; mặt cắt xác nhận hai đối tượng cùng khoảng cao độ.

### A8. Ống quá sát cột, không đủ chỗ lắp và hoàn thiện - P2

**Mô tả:** Ống không chạm cột nhưng không còn đủ khoảng cho bảo ôn, kẹp, thao
tác nối hoặc lớp hoàn thiện quanh cột.

**Hậu quả:** Lắp đặt khó, bề mặt hoàn thiện xấu, không bảo ôn được liên tục hoặc
không thể bảo trì mối nối.

**Cách người dùng nhận biết:** Khoảng cách thực giữa biên ống và mặt cột nhỏ hơn
không gian cần cho lớp bọc và thao tác thực tế.

### A9. Ống đi vào móng, đài móng hoặc giằng móng - P1

**Mô tả:** Tuyến ngầm giao thể tích móng, đài móng hoặc giằng móng, hoặc đi qua
vùng không có sleeve được chấp thuận.

**Hậu quả:** Không thể đào/lắp theo tuyến, nguy cơ làm ảnh hưởng kết cấu móng;
phải đổi tuyến khi công trường đã khó tiếp cận.

**Cách người dùng nhận biết:** Mặt bằng móng và cao độ tuyến ngầm cho thấy cùng
vị trí và cao độ; không có chi tiết xuyên móng được duyệt.

### A10. Ống chôn ngầm không đủ lớp phủ hoặc xung đột cao độ móng - P1

**Mô tả:** Đỉnh ống quá gần mặt đất/sàn hoặc đáy ống quá thấp, chạm bê tông lót,
móng hay cao độ đào cho phép.

**Hậu quả:** Ống dễ bị tải trọng hoặc thi công sau làm hư hỏng, không giữ được
độ dốc, phải đào sâu/thay đổi tuyến ngoài kế hoạch.

**Cách người dùng nhận biết:** Mặt cắt tuyến ngầm cho thấy lớp phủ không đủ hoặc
envelope ống giao vùng móng/bê tông lót.

## B. Ống với kiến trúc

### B1. Ống xuyên tường sai vị trí hoặc thiếu lỗ chờ - P1

**Mô tả:** Tuyến đi qua tường ngoài vị trí opening/sleeve đã phối hợp, hoặc vị
trí trên shopdrawing không khớp bản vẽ kiến trúc.

**Hậu quả:** Phải khoan/cắt sau, ảnh hưởng chống cháy, chống thấm, cách âm và bề
mặt hoàn thiện; dễ phát sinh sửa tại công trường.

**Cách người dùng nhận biết:** Giao điểm ống-tường không trùng lỗ chờ hoặc sai
kích thước/cao độ so với chi tiết được chấp thuận.

### B2. Ống xuyên tường chống cháy nhưng thiếu điều kiện xử lý - P1

**Mô tả:** Ống xuyên qua tường/vách có yêu cầu chống cháy nhưng không có đủ
khoảng hoặc chỉ dẫn để xử lý bịt kín theo yêu cầu dự án.

**Hậu quả:** Không đạt nghiệm thu chống cháy, phải tháo/sửa xuyên tường hoặc bổ
sung giải pháp sau khi hoàn thiện.

**Cách người dùng nhận biết:** Tuyến xuyên qua ranh giới chống cháy; vị trí xuyên
thiếu sleeve/khoảng trám hoặc thông tin xác nhận phù hợp.

### B3. Ống va chạm vách hoặc khung vách - P2

**Mô tả:** Ống đi trong/qua vách nhưng chạm stud, runner, lớp gia cường hoặc
không vừa trong chiều dày vách.

**Hậu quả:** Vách không đóng được, phải cắt khung hoặc làm hộp che; ảnh hưởng
tiến độ hoàn thiện và chất lượng bề mặt.

**Cách người dùng nhận biết:** Kích thước ngoài của ống lớn hơn khoang vách hoặc
vị trí tuyến trùng với vùng khung/gia cường đã biết.

### B4. Ống nằm dưới cao độ trần hoàn thiện - P1

**Mô tả:** Đáy ống, fitting, bảo ôn hoặc phụ kiện treo hạ xuống dưới mặt trần
hoàn thiện tại khu vực không cho phép lộ ống.

**Hậu quả:** Không đóng được trần, phải hạ trần, làm hộp che hoặc đổi toàn bộ cao
độ tuyến; ảnh hưởng trực tiếp kiến trúc phòng.

**Cách người dùng nhận biết:** Mặt cắt cho thấy phần thấp nhất của hệ ống thấp
hơn cao độ trần trong cùng khu vực.

### B5. Ống va chạm khung trần hoặc thiết bị trên trần - P2

**Mô tả:** Ống nằm trên mặt trần nhưng chạm khung xương, ty treo, đèn, miệng gió,
sprinkler hoặc thiết bị âm trần.

**Hậu quả:** Không thể hoàn thiện trần đúng bố trí, phải đổi vị trí thiết bị hoặc
tuyến; có thể phát hiện rất muộn khi lắp trần.

**Cách người dùng nhận biết:** Mặt bằng trần và mặt cắt cho thấy hai đối tượng
giao nhau hoặc không đủ khoảng lắp đặt.

### B6. Ống cản lỗ thăm trần hoặc đường tiếp cận - P2

**Mô tả:** Tuyến đi qua phía trên lỗ thăm, chắn đường đưa tay/dụng cụ hoặc che
khuất thiết bị cần kiểm tra.

**Hậu quả:** Không bảo trì được van, cửa thăm, thiết bị; phải tháo trần hoặc di
chuyển đường ống sau bàn giao.

**Cách người dùng nhận biết:** Vùng tiếp cận từ lỗ thăm tới thiết bị bị ống hoặc
fitting chiếm chỗ.

### B7. Tuyến không theo sàn giật cấp - P1

**Mô tả:** Cao độ ống được giữ theo sàn chung nhưng đi vào vùng sàn giật cấp có
mặt trên/mặt dưới khác, làm ống chạm sàn hoặc lộ khỏi vùng cho phép.

**Hậu quả:** Mất độ dốc, không đủ chiều dày che ống, phải đục sàn hoặc đổi tuyến
tại công trường.

**Cách người dùng nhận biết:** Tuyến cắt qua biên vùng giật cấp nhưng cao độ ống
không thay đổi phù hợp; mặt cắt cho thấy thiếu khoảng trống.

### B8. Ống hoặc fitting nằm đúng tại mép sàn giật cấp - P2

**Mô tả:** Mối nối, fitting hoặc đoạn chuyển cao độ nằm sát mép thay đổi sàn,
nơi không đủ không gian cho thân phụ kiện và thao tác.

**Hậu quả:** Khó định vị, không lắp được fitting như bản vẽ hoặc tạo điểm yếu về
chống thấm/hoàn thiện.

**Cách người dùng nhận biết:** Vị trí fitting/mối nối trùng hoặc quá gần đường
biên giật cấp trên mặt bằng.

### B9. Ống trong sàn gỗ/sàn nâng va chạm hệ đỡ - P2

**Mô tả:** Tuyến nằm trong khoang sàn nhưng giao chân đỡ, khung sàn, dầm phụ hoặc
vùng không được phép đặt ống.

**Hậu quả:** Không lắp được tấm sàn/khung đỡ, phải dịch tuyến hoặc thay đổi bố
trí hệ sàn.

**Cách người dùng nhận biết:** Mặt bằng bố trí chân/khung sàn cho thấy tuyến hoặc
fitting trùng vị trí; mặt cắt xác nhận cùng cao độ.

### B10. Ống trong sàn gỗ/sàn nâng không đủ chiều cao khoang - P1

**Mô tả:** Tổng kích thước ống, độ dốc, bảo ôn và giá đỡ lớn hơn chiều cao hữu
dụng của khoang sàn.

**Hậu quả:** Không đóng được sàn, ống chạm sàn kết cấu hoặc mặt dưới tấm sàn;
phải nâng sàn hoặc đổi hệ thống tuyến.

**Cách người dùng nhận biết:** Mặt cắt cho thấy envelope lắp đặt vượt ra ngoài
khoang hữu dụng tại một hoặc nhiều điểm trên tuyến.

## C. Ống với MEP khác

### C1. Hai ống va chạm vật lý - P1

**Mô tả:** Thân ống, bảo ôn hoặc fitting của hai tuyến chiếm cùng không gian.

**Hậu quả:** Một trong hai hệ không lắp được; phải thay đổi cao độ/thứ tự hoặc
đi lại tuyến, có thể ảnh hưởng độ dốc và điểm kết nối.

**Cách người dùng nhận biết:** Giao nhau trên mặt bằng và mặt cắt xác nhận khoảng
cao độ chồng lấn; hoặc hai tuyến chạy song song nhưng khoảng cách quá nhỏ.

### C2. Hai ống không chạm nhưng thiếu khoảng thi công - P2

**Mô tả:** Khoảng giữa hai tuyến không đủ cho bảo ôn, kẹp, nối ống hoặc dung sai
lắp đặt.

**Hậu quả:** Lắp đặt khó, bảo ôn bị ép/gián đoạn, không thao tác được tại mối nối
và dễ phải dịch tuyến tại công trường.

**Cách người dùng nhận biết:** Khoảng hở thực giữa hai envelope nhỏ hơn yêu cầu
thi công của loại ống/vật liệu liên quan.

### C3. Fitting của hai hệ chồng vùng thao tác - P2

**Mô tả:** Đoạn thẳng không va chạm nhưng van, cleanout, reducer, nhánh hoặc mối
nối của hai tuyến tranh cùng không gian thao tác.

**Hậu quả:** Không lắp hoặc không bảo trì được phụ kiện; phải thay đổi vị trí
fitting sau khi tuyến chính đã cố định.

**Cách người dùng nhận biết:** Vùng quanh fitting/mối nối bị một tuyến khác đi
qua hoặc che đường tiếp cận.

### C4. Ống va chạm ống gió - P1

**Mô tả:** Ống hoặc fitting giao thân ống gió, lớp bảo ôn, mặt bích hoặc phụ kiện
ống gió.

**Hậu quả:** Không lắp được một trong hai hệ; ống gió thường chiếm không gian lớn
nên thay đổi muộn có thể kéo theo nhiều nhánh và thiết bị.

**Cách người dùng nhận biết:** Mặt bằng cho thấy giao tuyến và mặt cắt cho thấy
envelope ống chồng envelope ống gió/phụ kiện.

### C5. Ống đi qua vùng mặt bích hoặc cửa bảo trì ống gió - P2

**Mô tả:** Không chạm thân ống gió nhưng chắn vị trí nối mặt bích, cửa kiểm tra,
damper hoặc vùng cần tháo lắp.

**Hậu quả:** Không siết/lắp được mặt bích, không mở cửa kiểm tra hoặc không bảo
trì được damper sau hoàn thiện.

**Cách người dùng nhận biết:** Tuyến ống đi qua vùng thao tác quanh mặt bích/cửa
kiểm tra dù hai thân vật thể chưa giao nhau.

### C6. Ống va chạm máng cáp hoặc thang cáp - P1

**Mô tả:** Ống, bảo ôn, fitting hoặc giá treo giao máng/thang cáp và phụ kiện của
hệ điện.

**Hậu quả:** Không thể lắp đúng cao độ; thay đổi thứ tự trên/dưới có thể ảnh
hưởng an toàn, bảo trì và quy định riêng của dự án.

**Cách người dùng nhận biết:** Hai hệ giao nhau trong cùng khoảng cao độ hoặc
chạy song song không đủ khoảng cách.

### C7. Tuyến nước đặt trên thiết bị điện/máng cáp không phù hợp - P1

**Mô tả:** Tuyến có nguy cơ rò nước nằm trực tiếp phía trên tủ điện, thiết bị
điện hoặc khu vực mà dự án không cho phép.

**Hậu quả:** Nước rò có thể gây hư hỏng thiết bị, mất điện hoặc mất an toàn; khó
được chấp thuận khi kiểm tra phối hợp.

**Cách người dùng nhận biết:** Hình chiếu tuyến nằm trong vùng phía trên thiết bị
điện/máng cáp và thuộc loại hệ có rủi ro rò nước theo rule dự án.

### C8. Ống va chạm thân thiết bị - P1

**Mô tả:** Tuyến hoặc fitting đi vào phạm vi thực của bơm, AHU, bồn, tủ hoặc
thiết bị MEP khác.

**Hậu quả:** Thiết bị không đặt được đúng vị trí, không nối được hoặc phải đổi
tuyến/đế thiết bị sau khi đã thi công.

**Cách người dùng nhận biết:** Envelope ống giao phạm vi chiếm chỗ của thiết bị
trên mặt bằng và theo chiều cao.

### C9. Ống cản cửa mở hoặc vùng bảo trì thiết bị - P1

**Mô tả:** Ống không chạm thân thiết bị nhưng nằm trong vùng mở cửa, rút filter,
tháo motor, vận hành van hoặc tiếp cận bảo trì.

**Hậu quả:** Thiết bị vẫn lắp được nhưng không vận hành/bảo trì đúng; có thể phải
di chuyển tuyến sau khi bàn giao.

**Cách người dùng nhận biết:** Tuyến đi qua vùng thao tác được chỉ định quanh
thiết bị hoặc chắn đường tiếp cận từ lối đi/lỗ thăm.

### C10. Điểm nối ống không khớp điểm chờ của thiết bị - P1

**Mô tả:** Vị trí, cao độ, hướng hoặc kích thước đầu ống không khớp nozzle/đầu
chờ thực tế của thiết bị.

**Hậu quả:** Không kết nối được, phải chế thêm đoạn chuyển, dịch thiết bị hoặc
sửa tuyến; dễ tạo ứng suất và giảm chất lượng lắp đặt.

**Cách người dùng nhận biết:** So sánh đầu tuyến với thông tin điểm kết nối cho
thấy sai tọa độ, cao độ, hướng hoặc kích thước.

## D. Ống chờ xuyên cấu kiện

### D1. Thiếu ống chờ/sleeve tại vị trí tuyến xuyên - P1

**Mô tả:** Shopdrawing có tuyến xuyên sàn/tường nhưng bản vẽ sleeve hoặc danh
sách lỗ chờ không có vị trí tương ứng.

**Hậu quả:** Bê tông/tường hoàn thành trước khi phát hiện; phải khoan cắt, xin
phê duyệt bổ sung và sửa chống thấm/chống cháy.

**Cách người dùng nhận biết:** Mỗi giao điểm tuyến-cấu kiện không tìm thấy ống
chờ có vị trí và cao độ tương ứng.

### D2. Có ống chờ nhưng sai vị trí mặt bằng - P1

**Mô tả:** Tâm sleeve/lỗ chờ lệch so với tâm tuyến hoặc fitting đến mức không
thể hấp thụ bằng dung sai lắp đặt.

**Hậu quả:** Ống không đi qua được, phải bẻ lệch không hợp lý, mở rộng lỗ hoặc
dịch tuyến.

**Cách người dùng nhận biết:** Khoảng lệch tâm giữa tuyến và ống chờ vượt dung
sai được dự án chấp nhận.

### D3. Ống chờ sai cao độ hoặc sai tầng - P1

**Mô tả:** Sleeve xuyên tường/dầm hoặc đầu chờ đứng được đặt ở cao độ/tầng khác
với tuyến cần kết nối.

**Hậu quả:** Không sử dụng được lỗ chờ, phải khoan bổ sung hoặc thay đổi cao độ
tuyến gây mất độ dốc và va chạm mới.

**Cách người dùng nhận biết:** Cao độ/tầng của sleeve không trùng phạm vi xuyên
của tuyến tại cùng vị trí mặt bằng.

### D4. Ống chờ sai kích thước - P1

**Mô tả:** Đường kính hoặc kích thước opening không đủ cho ống, bảo ôn, độ lệch
lắp đặt và vật liệu trám kín.

**Hậu quả:** Không luồn được ống hoặc không thể hoàn thiện chống cháy/chống thấm
đúng yêu cầu.

**Cách người dùng nhận biết:** Kích thước hữu dụng của ống chờ nhỏ hơn tổng kích
thước cần thiết của tuyến và khoảng xử lý xung quanh.

### D5. Ống chờ sai hướng hoặc không vuông góc phù hợp - P2

**Mô tả:** Sleeve được đặt theo hướng không phù hợp với hướng tuyến, đặc biệt tại
ống nghiêng hoặc tường dày.

**Hậu quả:** Thân ống chạm mép sleeve, không đủ khoảng trám hoặc phải tạo đoạn
chuyển ngay sát cấu kiện.

**Cách người dùng nhận biết:** Trục sleeve và trục tuyến khác hướng đáng kể;
mặt cắt cho thấy ống chạm mép tại đầu vào/ra.

### D6. Nhiều tuyến tranh cùng một lỗ chờ - P1

**Mô tả:** Hai hoặc nhiều ống được bố trí qua cùng opening nhưng không đủ diện
tích, khoảng cách giữa ống hoặc không đáp ứng điều kiện trám kín.

**Hậu quả:** Không thể lắp đủ tuyến, không xử lý chống cháy/chống thấm đúng hoặc
phải mở rộng lỗ ngoài phê duyệt.

**Cách người dùng nhận biết:** Tổng envelope các ống và khoảng cách yêu cầu vượt
phạm vi hữu dụng của opening.

### D7. Ống chờ trùng thép/khu vực kết cấu cấm - P1

**Mô tả:** Vị trí sleeve được đề xuất nằm trong vùng kết cấu không cho phép hoặc
không có xác nhận của bộ môn kết cấu.

**Hậu quả:** Sleeve bị từ chối hoặc không thể đặt trước khi đổ bê tông; thay đổi
muộn ảnh hưởng tuyến và tiến độ.

**Cách người dùng nhận biết:** Vị trí nằm trong vùng cấm/không được phê duyệt
trên bản vẽ kết cấu hoặc thiếu trạng thái xác nhận cần thiết.

### D8. Đầu ống chờ bị vật thể khác che hoặc không thao tác được - P2

**Mô tả:** Sleeve đúng vị trí nhưng đầu ra bị dầm, tường, trần, thiết bị hoặc hệ
MEP khác chắn, không đủ chỗ nối tiếp.

**Hậu quả:** Không thể kéo/luồn/nối ống sau khi cấu kiện hoàn thành; phải xử lý
đoạn chuyển khó thi công.

**Cách người dùng nhận biết:** Vùng ngay trước và sau sleeve bị vật thể khác
chiếm chỗ hoặc không đủ chiều dài thao tác.

## E. Độ dốc và thoát nước

### E1. Độ dốc ngược hướng thoát - P1

**Mô tả:** Cao độ tuyến tăng theo hướng dòng chảy thay vì giảm về điểm thu/điểm
thoát.

**Hậu quả:** Nước không thoát, đọng nước, tắc nghẽn và có thể phải tháo toàn bộ
đoạn tuyến.

**Cách người dùng nhận biết:** So sánh hướng dòng chảy với cao độ đầu-cuối cho
thấy đoạn ống dốc ngược.

### E2. Độ dốc nhỏ hơn yêu cầu của dự án - P1

**Mô tả:** Tuyến dốc đúng hướng nhưng mức giảm cao độ trên chiều dài không đạt
giá trị đã được chọn cho loại ống/hệ thống.

**Hậu quả:** Dòng chảy kém, dễ đọng cặn và tắc; không đạt kiểm tra trước phát
hành hoặc nghiệm thu.

**Cách người dùng nhận biết:** Tỷ lệ giữa chênh cao đầu-cuối và chiều dài thực
nhỏ hơn rule `1/N` hoặc yêu cầu đã xác nhận của dự án.

### E3. Độ dốc quá lớn làm mất cao độ không gian - P2

**Mô tả:** Tuyến giảm cao độ nhiều hơn cần thiết, làm đầu cuối xuống quá thấp dù
vẫn thoát nước.

**Hậu quả:** Chạm trần, dầm, hệ khác hoặc không kết nối được điểm đích; lãng phí
không gian trần.

**Cách người dùng nhận biết:** Độ dốc vượt phạm vi áp dụng của dự án hoặc cao độ
cuối tuyến thấp hơn không gian cho phép.

### E4. Mất độ dốc tại một đoạn cục bộ - P1

**Mô tả:** Tổng thể tuyến có vẻ đúng nhưng một đoạn giữa hai node/fitting bị
ngang, dốc ngược hoặc tạo điểm võng.

**Hậu quả:** Nước đọng cục bộ, tích cặn và khó phát hiện nếu chỉ xem cao độ đầu
toàn tuyến.

**Cách người dùng nhận biết:** Kiểm tra liên tục từng đoạn cho thấy cao độ không
giảm đều theo hướng dòng chảy.

### E5. Điểm cao/điểm thấp ngoài ý muốn tại fitting - P1

**Mô tả:** Vị trí nhánh, reducer, elbow hoặc fitting tạo túi nước/điểm giữ khí do
cao độ các đầu nối không liên tục.

**Hậu quả:** Thoát nước không ổn định, đọng cặn hoặc không xả hết; phải chỉnh
fitting và các đoạn kề.

**Cách người dùng nhận biết:** Profile cao độ qua fitting đổi chiều hoặc có một
đầu nối cao/thấp bất thường so với các đoạn trước-sau.

### E6. Nhánh đấu vào tuyến chính sai cao độ hoặc sai hướng - P1

**Mô tả:** Nhánh thoát nước nối vào tuyến chính tại cao độ/hướng làm cản dòng,
gây dốc ngược hoặc không phù hợp cách đấu nối đã chọn.

**Hậu quả:** Dễ tắc, chảy ngược vào nhánh hoặc không lắp được fitting đúng quy
cách.

**Cách người dùng nhận biết:** Cao độ và hướng của nhánh tại fitting không liên
tục với hướng dòng chảy của tuyến chính.

### E7. Không đủ chênh cao để tới điểm kết nối - P1

**Mô tả:** Với chiều dài và độ dốc cần thiết, tuyến không thể đi từ điểm đầu tới
cao độ điểm cuối trong không gian hiện có.

**Hậu quả:** Không thể vừa giữ độ dốc vừa tránh dầm/trần; phải đổi đường đi, điểm
kết nối hoặc phương án hệ thống.

**Cách người dùng nhận biết:** Cao độ yêu cầu tại điểm cuối khác cao độ kết nối
thực tế sau khi tính theo chiều dài tuyến và độ dốc.

### E8. Tuyến đúng độ dốc nhưng va chạm dọc đường - P1

**Mô tả:** Đầu và cuối tuyến phù hợp, nhưng profile nghiêng của thân ống đi qua
dầm, sàn, trần hoặc hệ MEP khác tại một vị trí trung gian.

**Hậu quả:** Shopdrawing nhìn điểm đầu-cuối có vẻ đúng nhưng không thể thi công;
đổi cao độ cục bộ có thể làm mất độ dốc.

**Cách người dùng nhận biết:** Kiểm tra cao độ liên tục dọc tuyến cho thấy
envelope ống giao vật thể tại khoảng giữa đoạn.

### E9. Sai cao độ đáy/tâm/đỉnh ống do hiểu nhầm mốc - P1

**Mô tả:** Giá trị cao độ được ghi hoặc sử dụng theo tim ống trong khi bản vẽ/yêu
cầu đang nói về đáy hoặc đỉnh ống, hoặc ngược lại.

**Hậu quả:** Toàn tuyến bị lệch theo bán kính/kích thước ống; gây sai kết nối,
va chạm và mất khoảng trần.

**Cách người dùng nhận biết:** So sánh quy ước cao độ với kích thước ống và mặt
cắt cho thấy vị trí thân ống không khớp giá trị ghi chú.

### E10. Tuyến thoát nước có đoạn chết hoặc đầu hở ngoài ý muốn - P1

**Mô tả:** Graph tuyến có đoạn không dẫn tới điểm thoát, đầu ống chưa kết nối
hoặc nhánh cụt không phải cleanout/đầu chờ được chủ ý bố trí.

**Hậu quả:** Hệ thống không hoạt động đầy đủ, rò nước khi thử hoặc bỏ sót kết nối
trước khi đóng trần/sàn.

**Cách người dùng nhận biết:** Theo hướng dòng chảy, một nhánh kết thúc mà không
gặp điểm thoát, thiết bị, cleanout hoặc đầu chờ đã được xác nhận.

### E11. Thiếu khả năng vệ sinh tại đoạn dễ tắc - P2

**Mô tả:** Tuyến dài, đổi hướng hoặc có điểm nguy cơ tích cặn nhưng không có vị
trí vệ sinh/tiếp cận theo yêu cầu của dự án.

**Hậu quả:** Khó xử lý tắc nghẽn sau bàn giao, phải mở trần/tường hoặc tháo tuyến.

**Cách người dùng nhận biết:** Đoạn tuyến và các lần đổi hướng vượt điều kiện
kiểm tra đã xác nhận nhưng không có cleanout hoặc access phù hợp.

### E12. Cleanout có nhưng không thể tiếp cận - P1

**Mô tả:** Cleanout bị quay vào tường, nằm trên trần không có lỗ thăm, bị hệ khác
che hoặc không đủ khoảng mở nắp/thao tác.

**Hậu quả:** Không vệ sinh được khi tắc; vị trí tồn tại trên bản vẽ nhưng vô dụng
trong vận hành thực tế.

**Cách người dùng nhận biết:** Hướng mở và vùng thao tác của cleanout giao vật
thể khác hoặc không nối tới khu vực có thể tiếp cận.

## 3. Cách sử dụng catalog khi kiểm tra bản vẽ

Mỗi lỗi được phát hiện cần giúp người kiểm tra trả lời bốn câu hỏi thực tế:

1. Lỗi nằm ở tầng, khu vực và vị trí nào?
2. Ống đang xung đột với đối tượng nào?
3. Hậu quả nếu phát hành hoặc thi công nguyên trạng là gì?
4. Đây là lỗi chắc chắn, trường hợp cần xác nhận hay vùng thiếu dữ liệu?

Không được coi “không phát hiện lỗi” là “thi công được” khi bản vẽ thiếu cao độ,
kích thước cấu kiện, thông tin lỗ chờ hoặc phạm vi thiết bị. Trong trường hợp đó,
người dùng phải nhận được cảnh báo cần bổ sung hoặc xác nhận dữ liệu trước khi
phát hành.

## 4. Ngoài phạm vi tài liệu

Catalog này không quy định giải pháp kỹ thuật, cấu trúc phần mềm hoặc cách tự
động sửa tuyến. Quyết định thay đổi cao độ, mở lỗ, xuyên kết cấu hoặc điều chỉnh
thiết bị vẫn phải được người có trách nhiệm và các bộ môn liên quan xác nhận.
