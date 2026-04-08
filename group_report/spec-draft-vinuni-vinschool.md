# SPEC draft — C401 - D5 · Track C (VinUni / VinSchool)

Bản nháp SPEC cho hackathon (Canvas, User stories 4 paths, Eval, Failure modes, ROI, Mini AI spec).

**Nhóm D5:**

| Họ tên | MSSV |
|--------|------|
| Đào Phước Thịnh | 2A202600029 |
| Nguyễn Tri Nhân | 2A202600224 |
| Trần Xuân Trường | 2A202600321 |
| Hồ Sỹ Minh Hà | 2A202600060 |
| Nông Nguyễn Thành | 2A202600250 |
| Đào Văn Công | 2A202600031 |
| Đặng Hồ Hải | 2A202600020 |

---

## Dự án / track

| | |
|--|--|
| **Track** | **C — VinUni / VinSchool** |
| **Domain** | AI trợ lý nghiệp vụ nội bộ — truy vấn dữ liệu sinh viên & soạn thảo truyền thông hàng loạt |

**Tên ý tưởng / working title:** _StudentOps AI_ — Trợ lý nghiệp vụ sinh viên bằng ngôn ngữ tự nhiên

---

## Actors

| Actor | Vai trò |
|-------|---------|
| **Phòng Cộng Tác Sinh Viên** | Truyền thông, thông báo sự kiện, hỗ trợ sinh viên — thường xuyên cần gửi email theo nhóm/điều kiện |
| **Phòng Đào Tạo** | Quản lý học vụ, điểm số, tình trạng học tập — thường xuyên cần lọc danh sách sinh viên theo tiêu chí phức tạp |

---

## Use Cases

### Use Case 1: Truy vấn dữ liệu sinh viên bằng ngôn ngữ tự nhiên

Người dùng nhập yêu cầu bằng ngôn ngữ tự nhiên ("Lấy danh sách sinh viên K67 chưa đóng học phí học kỳ này"). Hệ thống chuyển đổi thành truy vấn, trả về kết quả dạng bảng. Người dùng xem kết quả, có thể tinh chỉnh yêu cầu, và tải xuống CSV/Excel.

**Có thể mở rộng:** Từ kết quả truy vấn, người dùng có thể kích hoạt Use Case 2 (soạn email cho danh sách này) hoặc các hành động khác (xuất báo cáo, lấy bảng điểm, tạo danh sách dự kiến tốt nghiệp...).

### Use Case 2: Soạn và gửi email từ dữ liệu sinh viên (có HIL)

Người dùng yêu cầu hệ thống tạo nội dung email dựa trên danh sách sinh viên (từ kết quả UC1 hoặc nhập trực tiếp). Hệ thống hiển thị danh sách người nhận và nội dung email draft để người dùng xem xét và chỉnh sửa. Người dùng xác nhận (Human-in-the-Loop) trước khi gửi hàng loạt. Hệ thống ghi nhận trạng thái gửi.

---

## 1. Problem statement

**User:** Nhân viên Phòng Cộng Tác Sinh Viên và Phòng Đào Tạo tại VinUni/VinSchool.

**Pain hiện tại:**
- Truy vấn dữ liệu sinh viên theo tiêu chí phức tạp (VD: "sinh viên K67, GPA < 2.0, chưa đăng ký môn học kỳ này") yêu cầu SQL hoặc phụ thuộc bộ phận IT → chậm, phụ thuộc, không linh hoạt.
- Soạn email hàng loạt mang tính cá nhân hoá (kèm tên, mã SV, thông tin riêng) phải làm thủ công từ Excel → tốn thời gian, dễ sai sót.
- Không có luồng kiểm soát rõ ràng trước khi gửi → rủi ro gửi nhầm, gửi thiếu.

**AI đóng vai trò gì mà cách hiện tại không làm được:**
- Dịch ngôn ngữ tự nhiên thành truy vấn chính xác theo thời gian thực, không cần SQL.
- Tạo nội dung email draft có cá nhân hoá theo từng sinh viên (merge field) trong vài giây.
- Cung cấp điểm kiểm soát HIL rõ ràng trước mỗi hành động có tác động thực (gửi email, xuất báo cáo chính thức).

---

## 2. Canvas draft

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost/request? Latency? Risk chính? |
| **Trả lời** | **UC1:** Nhân viên phòng ban cần lọc dữ liệu nhanh mà không biết SQL. Pain: phụ thuộc IT, chậm, không linh hoạt. AI dịch NL → query → trả bảng kết quả ngay. **UC2:** Soạn email hàng loạt cá nhân hoá mất hàng giờ. AI draft nội dung + danh sách nhận trong vài giây. | **UC1 sai:** Truy vấn sai → data sai → quyết định sai (VD: nhắn nhở sai người). Người dùng biết qua: hiển thị query đã dịch để xác nhận + preview kết quả. Sửa bằng: tinh chỉnh prompt hoặc edit query trực tiếp. **UC2 sai:** Email gửi sai nội dung / sai người → ảnh hưởng uy tín. Ngăn bằng HIL: preview đầy đủ trước khi confirm gửi. | **Cost:** ~$0.01–0.05/query (LLM API). **Latency:** 2–5 giây/query. **Risk chính:** NL-to-SQL sai (wrong data), LLM hallucinate nội dung email, SQL injection qua NL input. **Giảm thiểu:** read-only DB, schema validation, HIL bắt buộc trước send. |

**Automation hay augmentation?** ☑ **Augmentation** cho cả 2 UC

**Justify:** UC1 — AI dịch query và trả kết quả, nhưng người dùng xem preview và quyết định dùng data đó. UC2 — AI draft email và danh sách, nhưng HIL bắt buộc trước khi gửi. Nếu AI sai → người dùng kịp can thiệp, không có thiệt hại đã xảy ra.

Agency progression: V1 (augmentation, HIL toàn phần) → V2 (semi-auto với threshold confidence cao, HIL cho edge cases) → V3 (auto với monitoring) khi có đủ data xác nhận accuracy.

**Learning signal:**
- **Implicit:** Người dùng có refine query không (số lần retry = tín hiệu query sai)
- **Explicit:** Thumbs up/down sau khi xem kết quả query; rating email draft
- **Correction:** Người dùng edit query trực tiếp / chỉnh nội dung email → dữ liệu vàng để fine-tune

---

## 3. User stories — 4 paths (UX)

### Use Case 1: Truy vấn dữ liệu

#### 3.1.1 AI đúng (Happy path)

> *"Với tư cách là nhân viên Phòng Đào Tạo, tôi nhập 'Sinh viên K67 GPA dưới 2.0 học kỳ vừa rồi', hệ thống trả về bảng danh sách đúng, tôi tải CSV và tiến hành bước tiếp theo."*

UI: Hiển thị query đã dịch (dạng text dễ đọc, không phải SQL thô) + bảng kết quả với row count rõ ràng. Nút "Tải xuống CSV" và "Gửi email cho danh sách này" luôn hiển thị.

#### 3.1.2 AI không chắc (Low-confidence)

Hệ thống phát hiện query có thể hiểu theo nhiều cách (VD: "sinh viên có vấn đề" — vấn đề gì?). UI hiển thị cảnh báo mức độ tin cậy + 2–3 interpretation để người dùng chọn. Không tự chọn, không im lặng.

#### 3.1.3 AI sai (Failure path)

Người dùng xem bảng kết quả và nhận ra thiếu/sai dữ liệu. UI: Hiển thị query đã dịch nổi bật → người dùng có thể nhấn "Sửa yêu cầu" (refine NL) hoặc "Chỉnh query" (edit trực tiếp nếu biết SQL). Row count lớn/nhỏ bất thường → system tự cảnh báo "Kết quả có vẻ bất thường — kiểm tra lại yêu cầu?"

#### 3.1.4 User sửa / mất niềm tin / thoát an toàn

Người dùng không tin kết quả → có thể "Xem lại query gốc", "Export và kiểm tra thủ công", hoặc "Liên hệ IT để xác nhận". Không có dead end. Mọi thao tác đều reversible.

---

### Use Case 2: Soạn và gửi email

#### 3.2.1 AI đúng (Happy path)

> *"Với tư cách là nhân viên Phòng Cộng Tác Sinh Viên, tôi yêu cầu 'Soạn email nhắc nhở sinh viên chưa đóng học phí', AI draft nội dung có merge field {{tên}}, {{mã SV}}, {{số tiền}}, tôi xem preview, ưng, nhấn Gửi."*

UI: HIL screen hiển thị (1) danh sách người nhận với sample 5–10 người đầu, (2) preview email với dữ liệu thật của 1 người, (3) nút "Xem tất cả", "Chỉnh sửa nội dung", "Xác nhận gửi" với warning "Hành động này không thể thu hồi".

#### 3.2.2 AI không chắc (Low-confidence)

AI không đủ ngữ cảnh để viết email (VD: không rõ deadline, số tiền). System hiển thị draft với placeholder rõ ràng `[DEADLINE - cần điền]` thay vì hallucinate. Người dùng bắt buộc điền trước khi Gửi được kích hoạt.

#### 3.2.3 AI sai (Failure path)

Người dùng phát hiện nội dung email sai (tông sai, thông tin sai). UI: Editor đầy đủ để chỉnh sửa trực tiếp. Có thể "Soạn lại từ đầu", "Dùng template có sẵn", hoặc thoát và soạn bằng công cụ khác. Email chưa gửi cho đến khi người dùng nhấn Xác nhận lần cuối.

#### 3.2.4 User sửa / mất niềm tin / thoát an toàn

Người dùng không tin AI draft → có thể xoá toàn bộ nội dung AI và tự viết (hệ thống vẫn giữ merge field logic). Hoặc thoát, lưu draft để xem lại sau. Không mất dữ liệu.

**Path yếu nhất cần ưu tiên thiết kế:** UC2 — Path 3 (AI sai, email gửi sai nội dung hàng loạt) và Path 2 (AI không chắc, hallucinate thông tin quan trọng). HIL là cơ chế phòng thủ chính — phải thiết kế kỹ màn hình xác nhận để người dùng thực sự đọc, không nhấn Gửi theo quán tính.

---

## 4. Eval metrics

| Metric | Định nghĩa | Mục tiêu / threshold | Cách đo |
|--------|------------|----------------------|---------|
| NL-to-Query precision | Tỉ lệ query dịch ra khớp intent người dùng (không cần refine) | ≥ 85% ở câu hỏi phổ biến | Ghi lại: query gốc + kết quả + có refine không; đánh giá thủ công 50 mẫu/tuần |
| Retry rate | % lần người dùng phải refine query ≥ 2 lần | ≤ 15% | Log từ hệ thống |
| Email draft acceptance rate | % email draft được gửi không chỉnh sửa nội dung | ≥ 60% (target), không phải càng cao càng tốt — cần người dùng thực sự đọc | Log trước/sau edit |
| HIL stop rate | % lần người dùng dừng ở màn hình xác nhận, không gửi | Theo dõi theo thời gian — tăng đột biến = vấn đề data/draft quality | Log từ hệ thống |
| Task time reduction | Thời gian hoàn thành tác vụ so với quy trình thủ công | Giảm ≥ 50% thời gian trung bình | Khảo sát + timed test với 5 user |
| Wrong send rate | Số lần email gửi nhầm nội dung / nhầm người | 0 — đây là hard requirement | Incident log |

**Ưu tiên precision hơn recall cho UC2:** Sai nhầm (gửi email sai) tệ hơn bỏ sót (chưa gửi được). Cơ chế HIL là hàng rào cuối cùng.

---

## 5. Failure modes

| Failure mode | Trigger | Tác động user | Phát hiện / giảm thiểu |
|--------------|---------|---------------|------------------------|
| **NL-to-SQL sai ngữ nghĩa** | Query mơ hồ, schema phức tạp, tên cột không khớp | Người dùng tin dữ liệu sai → quyết định sai | Hiển thị query đã dịch để user xác nhận; cảnh báo row count bất thường; read-only DB |
| **AI hallucinate thông tin trong email** | LLM tự bịa số tiền, deadline, tên chương trình không có trong context | Email gửi thông tin sai hàng loạt | Bắt buộc HIL; placeholder thay vì hallucinate; chỉ dùng data từ query result, không để LLM suy diễn |
| **Gửi nhầm danh sách người nhận** | Query sai → danh sách sai → user không kiểm tra kỹ | Email đến sai đối tượng, ảnh hưởng uy tín | HIL screen hiển thị sample người nhận thật; warning số lượng bất thường; không có "Gửi tất cả" 1 click |
| **SQL injection qua NL input** | User nhập NL chứa câu lệnh SQL | Rủi ro bảo mật database | Sanitize input; parameterized queries; read-only DB account; không expose raw SQL cho user thường |
| **Over-trust — user không đọc HIL** | UX confirmation quá đơn giản → click qua nhanh | Mất hiệu quả của HIL, fail mode vẫn xảy ra | Thiết kế HIL friction có chủ đích: hiển thị số người nhận lớn, preview email với data thật, checkbox xác nhận đã đọc |
| **Alexa Effect — data quality kém → AI càng kém** | Ít người dùng, ít correction signal, model không improve | Loop đi xuống | Bắt đầu scope nhỏ (1 phòng ban, 1 loại query); thu correction data từ sớm |

---

## 6. ROI (3 kịch bản)

**Giả định cơ sở:**
- 2 phòng ban, ~5 nhân viên dùng thường xuyên
- Hiện tại: 1 truy vấn phức tạp = 30–60 phút (chờ IT hoặc tự làm Excel); 1 email hàng loạt cá nhân hoá = 2–4 giờ
- Sau khi có tool: ~5 phút/query, ~15 phút/email campaign (bao gồm review HIL)
- Chi phí AI: ~$0.02–0.05/query (LLM API); ~$10–30/tháng cho volume hiện tại

| Kịch bản | Mô tả | Kết quả ước tính |
|----------|--------|-----------------|
| **Best** | Adoption cao (5 user, 10+ query/ngày), query accuracy cao (>90%), staff tiết kiệm 3–4h/ngày/người | Tiết kiệm ~600h/năm; ROI dương sau 1 tháng; data flywheel bắt đầu |
| **Base** | Adoption vừa (3 user, 3–5 query/ngày), accuracy 80%, cần refine thường xuyên | Tiết kiệm ~200h/năm; break-even sau 3 tháng; useful nhưng không transformative |
| **Worst** | Adoption thấp (1–2 user), accuracy <70%, user mất tin và quay lại thủ công | Không tiết kiệm thời gian thực; chi phí duy trì > lợi ích; cân nhắc dừng sau 2 tháng |

**Kill criteria:** Nếu sau 2 tháng retry rate > 40% (query sai quá nhiều) hoặc wrong send rate > 0 (email gửi sai), dừng UC2 và review lại NL-to-SQL pipeline.

---

## 7. Mini AI spec

| Hạng mục | Nội dung |
|----------|----------|
| **Luồng chính — UC1** | Input: NL query text → LLM dịch sang SQL → Execute trên DB (read-only) → Trả bảng kết quả → User xem / tải / kích hoạt UC2 |
| **Luồng chính — UC2** | Input: Mục đích email (NL) + danh sách người nhận (từ UC1 hoặc manual) → LLM draft email với merge fields → HIL screen (preview + edit) → User xác nhận → Gửi qua email service → Log trạng thái |
| **Dữ liệu / knowledge cần** | Schema DB sinh viên (tên bảng, cột, quan hệ) — đưa vào system prompt; Dữ liệu mẫu query phổ biến (few-shot); Template email theo loại thông báo |
| **Model / công cụ** | LLM (GPT-4o hoặc Claude 3.5 Sonnet) cho NL-to-SQL và email drafting; Function calling để execute query an toàn; Email service (SMTP / SendGrid) cho UC2 |
| **Guardrail / policy** | DB account read-only — không UPDATE/DELETE; Sanitize NL input trước khi đưa vào prompt; HIL bắt buộc trước mọi email send; Log toàn bộ query và email sent với timestamp + user ID; Rate limit: max 100 người nhận/lần gửi ở V1 |
| **Không trong scope V1** | Tự động gửi email không có HIL; Truy cập dữ liệu tài chính nhạy cảm; Modify dữ liệu sinh viên |

---

## 8. Hướng đi chính (prototype hackathon)

- **Core loop:** NL input → query preview (dạng mô tả, không phải SQL thô) → bảng kết quả → nút "Gửi email cho danh sách này"
- **HIL screen UC2:** Màn hình xác nhận đủ friction — số người nhận, preview email với dữ liệu thật người đầu tiên, checkbox "Đã xem kỹ danh sách và nội dung", nút Gửi chỉ active sau khi tick
- **Error design first:** Thiết kế path khi query sai (show query đã dịch, nút refine) và path khi AI không chắc (show placeholder thay vì hallucinate) trước khi polish happy path
- **Scope nhỏ:** 1 schema cụ thể (sinh viên + học phí hoặc sinh viên + điểm), 3–5 loại query phổ biến nhất, 2–3 template email tiêu chuẩn

---

## 9. Phân công (tham chiếu)

Bảng tracking: [`assignment-tracking.md`](assignment-tracking.md)
