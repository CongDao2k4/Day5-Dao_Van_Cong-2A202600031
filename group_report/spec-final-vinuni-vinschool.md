# SPEC FINAL — C401 - D5 · Track C (VinUni / VinSchool)

**StudentOps AI — Trợ lý nghiệp vụ sinh viên bằng ngôn ngữ tự nhiên**

Bản SPEC hoàn chỉnh cho hackathon: Canvas đầy đủ, User stories 4 paths, Eval metrics, Failure modes, ROI analysis, và Mini AI spec.

---

## Nhóm D5

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

## Dự án / Track

| | |
|--|--|
| **Track** | **C — VinUni / VinSchool** |
| **Domain** | AI trợ lý nghiệp vụ nội bộ — truy vấn dữ liệu sinh viên & soạn thảo truyền thông hàng loạt |
| **Tên ý tưởng** | **StudentOps AI** — Trợ lý nghiệp vụ sinh viên bằng ngôn ngữ tự nhiên |

---

## Actors

| Actor | Vai trò | Pain điển hình |
|-------|---------|---------|
| **Phòng Cộng Tác Sinh Viên** | Truyền thông, thông báo sự kiện, hỗ trợ sinh viên | Thường xuyên cần gửi email theo nhóm/điều kiện (VD: nhắc nhở học phí, thông báo sự kiện) — phải soạn manual, mất hàng giờ |
| **Phòng Đào Tạo** | Quản lý học vụ, điểm số, tình trạng học tập | Thường xuyên cần lọc danh sách sinh viên theo tiêu chí phức tạp (VD: K67, GPA < 2.0, chưa đăng ký môn) — phải dùng SQL hoặc đợi IT |

---

## Use Cases

### Use Case 1: Truy vấn dữ liệu sinh viên bằng ngôn ngữ tự nhiên

**Sơ lược:**
Người dùng nhập yêu cầu bằng ngôn ngữ tự nhiên (VD: "Lấy danh sách sinh viên K67 chưa đóng học phí học kỳ này"). Hệ thống chuyển đổi thành truy vấn, thực thi trên database, trả về kết quả dạng bảng. Người dùng xem kết quả, có thể tinh chỉnh yêu cầu, và tải xuống CSV/Excel.

**Mở rộng & tích hợp:**
Từ kết quả truy vấn, người dùng có thể kích hoạt Use Case 2 (soạn email cho danh sách này) hoặc các hành động khác (xuất báo cáo, lấy bảng điểm, tạo danh sách dự kiến tốt nghiệp, v.v.).

### Use Case 2: Soạn và gửi email từ dữ liệu sinh viên (có Human-in-the-Loop)

**Sơ lược:**
Người dùng yêu cầu hệ thống tạo nội dung email dựa trên danh sách sinh viên (từ kết quả UC1 hoặc nhập trực tiếp). Hệ thống hiển thị danh sách người nhận và nội dung email draft để người dùng xem xét và chỉnh sửa. **Người dùng bắt buộc xác nhận (Human-in-the-Loop) trước khi gửi** hàng loạt. Hệ thống ghi nhận trạng thái gửi (sent, bounce, error, v.v.).

### Use Case 3: Xuất báo cáo phân tích từ dữ liệu sinh viên

**Sơ lược:**
Người dùng nhập yêu cầu bằng ngôn ngữ tự nhiên về báo cáo (VD: "Tạo báo cáo tổng hợp: bao nhiêu sinh viên K67 chưa đóng học phí, chia theo tình trạng, xu hướng theo thời gian"). Hệ thống thực thi query, tạo bảng tổng hợp + biểu đồ visualization (bar chart, pie chart), cho phép người dùng export PDF hoặc chia sẻ dashboard.

**Xử lý tương tự UC1:** NL → query + aggregation → kết quả hiển thị dạng bảng + chart. User có thể refine yêu cầu hoặc sửa trực tiếp.

**V1 scope:** Hỗ trợ báo cáo cơ bản (count, sum, average) với 1–2 chart type (bar, pie). Mở rộng V2: drill-down, comparison, trend analysis.

### Use Case 4: Tạo danh sách dự kiến tốt nghiệp

**Sơ lược:**
Phòng Đào Tạo cần xác định sinh viên sắp tốt nghiệp theo tiêu chí phức tạp (hoàn thành đủ tín chỉ + GPA ≥ ngưỡng + không nợ học phí + không học lỗi). Người dùng yêu cầu: *"Danh sách sinh viên có thể tốt nghiệp trong kỳ tới?"*. Hệ thống:
- Thực thi query kết hợp nhiều bảng (students, transcripts, payments)
- Hiển thị danh sách 3 cột chính: Tên, Mã SV, Tình trạng (Sẵn sàng / Chưa đủ tín chỉ / Nợ học phí)
- User có thể drill-down vào từng sinh viên để xem chi tiết yêu cầu còn thiếu
- Export về Excel để gửi cho Phòng Quản lý Tài chính và Ban Giám Hiệu

**V1 scope:** Basic eligibility check (tín chỉ + GPAssistanA + học phí). V2: Include thêm conditions (punishment, GPA by major, credit deadline).

### Use Case 5: Theo dõi trạng thái email campaign (Analytics)

**Sơ lược:**
Sau khi gửi email hàng loạt (UC2), nhân viên muốn biết: Bao nhiêu email sent thành công? Bounce rate? Open rate? Người dùng yêu cầu: *"Báo cáo email campaigns tuần này"*. Hệ thống hiển thị:
- Danh sách các campaign đã gửi (ngày, chủ đề, số người nhận, số delivered, bounce rate)
- Chart: trend delivered/bounce qua thời gian
- Option drill-down: xem chi tiết bounce list hoặc list email mở

**V1 scope:** Basic delivery tracking (sent / delivered / bounce). V2: Include open rate (nếu tích hợp email pixel), click rate, unsubscribe handling.

**Chỉ trong Phạm vi V1 (Hackathon):**
- Use Case 1 + 2 (core: NL query + email drafting with HIL)
- Use Case 3 (basic report with 1–2 chart)
- Use Case 4 + 5 (optional: implement nếu còn thời gian, hoặc roadmap V1.1)

---

## 1. Problem Statement

**Nhóm người dùng:** Nhân viên Phòng Cộng Tác Sinh Viên và Phòng Đào Tạo tại VinUni/VinSchool.

**Pain hiện tại:**
1. **Truy vấn data phức tạp:** Tiêu chí như "sinh viên K67, GPA < 2.0, chưa đăng ký môn học kỳ này" yêu cầu viết SQL chính xác hoặc phụ thuộc bộ phận IT → chậm, phụ thuộc, không linh hoạt.
2. **Email hàng loạt cá nhân hoá:** Soạn email kèm tên, mã SV, thông tin riêng phải làm thủ công từ Excel hoặc mail merge đơn giản → tốn thời gian (2–4 giờ/campaign), dễ sai sót, không chuyên nghiệp.
3. **Thiếu kiểm soát truước khi thực thi:** Không có luồng xác nhận rõ ràng → rủi ro gửi nhầm, gửi thiếu, ảnh hưởng uy tín và mối quan hệ với sinh viên.

**AI đóng vai trò gì mà cách hiện tại không làm được:**
- **Dịch ngôn ngữ tự nhiên → truy vấn chính xác** theo thời gian thực, không cần SQL.
- **Tạo nội dung email draft** có cá nhân hoá (merge field) trong vài giây.
- **Cung cấp điểm kiểm soát HIL rõ ràng** trước mỗi hành động có tác động thực (gửi email, xuất báo cáo chính thức).

---

## 2. Value/Trust/Feasibility Canvas

|   | **Value** | **Trust** | **Feasibility** |
|---|-----------|-----------|-----------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost/request? Latency? Risk chính? Giảm thiểu bằng cách nào? |
| **Trả lời (V1 focus: UC1+UC2)** | **UC1:** Nhân viên phòng ban cần lọc dữ liệu nhanh mà không biết SQL. Pain hiện tại: phụ thuộc IT, chậm (30–60 phút/query), không linh hoạt. AI dịch NL → query → trả bảng kết quả trong 2–5 giây. **UC2:** Soạn email hàng loạt cá nhân hoá mất hàng giờ (2–4h). AI draft nội dung + danh sách nhận trong vài giây, user refine, gửi trong 15 phút. **UC3+:** Báo cáo, danh sách tốt nghiệp, tracking email → mở rộng sau V1. | **UC1 sai:** Truy vấn dịch sai → dữ liệu sai → quyết định sai (VD: nhắn nhở sai người, bỏ sót sinh viên). Người dùng phát hiện qua: hệ thống hiển thị query đã dịch (dạng text dễ đọc) để xác nhận + preview kết quả + warning nếu row count bất thường. Sửa bằng: tinh chỉnh prompt hoặc edit query trực tiếp (nếu biết SQL). **UC2 sai:** Email gửi sai nội dung / sai người → ảnh hưởng uy tín, mối quan hệ với sinh viên. Ngăn bằng HIL bắt buộc: preview đầy đủ danh sách + nội dung với dữ liệu thật trước khi confirm gửi. Không có "Gửi nhanh". | **Cost:** ~$0.01–0.05/query (LLM API); ~$10–30/tháng cho volume hiện tại (5 user, 5–10 query/ngày). **Latency:** 2–5 giây/query, chấp nhận được. **Risk chính:** (1) NL-to-SQL sai ngữ nghĩa, (2) LLM hallucinate thông tin email, (3) SQL injection, (4) Over-trust — user không đọc HIL. **Giảm thiểu:** (1) Read-only DB, hiển thị query để xác nhận, cảnh báo row count; (2) Bắt buộc HIL, placeholder thay vì hallucinate; (3) Sanitize input, parameterized queries; (4) HIL friction: show số người nhận, preview email với data thật, checkbox đã đọc. |

**Automation hay Augmentation?** **Augmentation** cho cả 2 UC

**Justify:** 
- **UC1:** AI dịch query và trả kết quả, nhưng người dùng xem preview và quyết định dùng data đó. Nếu không tin → có thể refine hoặc liên hệ IT.
- **UC2:** AI draft email và danh sách, nhưng HIL bắt buộc trước khi gửi. Nếu AI sai → người dùng kịp can thiệp, không có thiệt hại đã xảy ra.

**Agency progression:** 
- **V1:** Augmentation, HIL toàn phần (user phải confirm mọi hành động)
- **V2:** Semi-auto với threshold confidence cao, HIL cho edge cases
- **V3:** Auto với monitoring vérô khi có đủ data xác nhận accuracy

**Learning signal:**
- **Implicit:** Số lần user refine query (retry = tín hiệu query sai)
- **Explicit:** Thumbs up/down sau khi xem kết quả; rating email draft
- **Correction:** User edit query trực tiếp / chỉnh nội dung email → dữ liệu vàng để fine-tune

---

## 3. User Stories — 4 Paths (Happy / Low-confidence / Failure / Recovery)

### Use Case 1: Truy vấn dữ liệu sinh viên

#### Path 1.1: AI đúng (Happy path)

> *"Với tư cách là nhân viên Phòng Đào Tạo, tôi nhập 'Sinh viên K67 GPA dưới 2.0 học kỳ vừa rồi', hệ thống trả về bảng danh sách đúng có 27 sinh viên, tôi xem mẫu vài dòng, tin tưởng, tải CSV và tiến hành bước tiếp theo (gửi email)."*

**UI/UX:**
- Hiển thị query đã dịch (dạng text dễ đọc, VD: "Sinh viên khóa 2023 với GPA < 2.0 trong kỳ vừa rồi", không phải SQL thô)
- Bảng kết quả với row count rõ ràng (VD: "27 kết quả")
- Nút "Tải xuống CSV", "Tải xuống Excel", "Gửi email cho danh sách này", "Tinh chỉnh yêu cầu" luôn hiển thị
- Thumbs up/down feedback

#### Path 1.2: AI không chắc (Low-confidence path)

Hệ thống phát hiện query có thể hiểu theo nhiều cách (VD: "sinh viên có vấn đề" — vấn đề gì? GPA thấp? Nợ học phí? Thành tích kém?). 

**UI/UX:**
- Hiển thị banner cảnh báo: "Yêu cầu mơ hồ — có thể dùng một trong những cách này:"
- Liệt kê 2–3 interpretations cụ thể với preview kết quả (VD: "Vấn đề = GPA < 2.0: 27 sinh viên" vs "Vấn đề = Nợ học phí: 12 sinh viên")
- User chọn 1, không tự động chọn, không im lặng

#### Path 1.3: AI sai (Failure path)

Người dùng xem bảng kết quả và nhận ra thiếu/sai dữ liệu. VD: yêu cầu "GPA < 2.0" nhưng hệ thống trả về 52 kết quả (quá nhiều) hoặc dữ liệu có sinh viên K68 (sai khóa).

**UI/UX:**
- Hiển thị query đã dịch nổi bật + warning tự động nếu row count lớn/nhỏ bất thường: "Kết quả có vẻ bất thường (52 sinh viên) — kiểm tra lại yêu cầu?"
- Nút "Sửa yêu cầu" (refine NL, gọi lại AI) hoặc "Chỉnh query" (edit trực tiếp SQL nếu user biết)
- Nút "Xem lại schema" (show tên bảng, cột để user hiểu rõ hơn)
- Nút "Liên hệ IT để xác nhận"

#### Path 1.4: User sửa / mất niềm tin / thoát an toàn

Người dùng không tin kết quả → có thể:

**UI/UX:**
- "Sửa yêu cầu" (refine prompt)
- "Xem lại query gốc" (show SQL nếu muốn)
- "Export dữ liệu này để kiểm tra thủ công"
- "Liên hệ IT để xác nhận"
- Thoát mà không mất dữ liệu (draft được lưu tự động)

---

### Use Case 2: Soạn và gửi email

#### Path 2.1: AI đúng (Happy path)

> *"Với tư cách là nhân viên Phòng Cộng Tác Sinh Viên, tôi yêu cầu 'Soạn email nhắc nhở sinh viên chưa đóng học phí', AI draft nội dung có merge field {{tên}}, {{mã SV}}, {{số tiền}}, {{deadline}}, tôi xem preview với 1 sinh viên thực tế, ưng, nhấn 'Xác nhận gửi' và hệ thống gửi cho 487 sinh viên."*

**UIX:**
- Màn hình xác nhận (HIL) hiển thị:
  1. **Danh sách người nhận:** Sample 5–10 người đầu (kèm tên, mã SV, email) + "Xem tất cả 487 người" (expand hoặc modal)
     ```
     - Nguyễn Văn A (2A20010001, vana@vinuni.edu.vn) — học phí còn: 5,000,000 VND
     - Trần Thị B (2A20010002, tranb@vinuni.edu.vn) — học phí còn: 3,000,000 VND
     - ...
     [Xem tất cả 487 người]
     ```
  2. **Preview email:** Render email với dữ liệu lần đầu:
     ```
     Subject: Nhắc nhở đóng học phí — Hạn chót 31/05/2024
     
     Kính gửi Nguyễn Văn A (2A20010001),
     
     Chúng tôi nhận thấy tài khoản học phí của em còn nợ 5,000,000 VND.
     Vui lòng đóng trước hạn chót 31/05/2024 để tránh ảnh hưởng đến đăng ký môn học kỳ tới.
     
     Liên hệ: Phòng Đào Tạo, ext. 1234
     
     Trân trọng,
     VinUni
     ```
  3. **Checkbox xác nhận:** "Đã xem kỹ danh sách người nhận (487 người) và nội dung email. Hành động này không thể thu hồi."
  4. **Nút "Xác nhận gửi"** (chỉ active sau khi tick checkbox)

- Sau khi gửi: hiển thị confirmation + linking tracking dashboard

#### Path 2.2: AI không chắc (Low-confidence path)

AI không đủ ngữ cảnh để viết email (VD: yêu cầu "Soạn email về học phí" nhưng không rõ deadline, số tiền).

**UI/UX:**
- System draft email với **placeholder rõ ràng** thay vì hallucinate:
  ```
  Kính gửi {{tên}},
  
  Chúng tôi nhận thấy tài khoản học phí của em còn nợ {{số tiền}}.
  Vui lòng đóng trước hạn chót [DEADLINE - cần điền] để tránh ảnh hưởng đến đăng ký môn học.
  ```
- Hiển thị cảnh báo: "Email chưa hoàn chỉnh — cần điền các trường sau:"
  - DEADLINE
- User bắt buộc điền trước khi nút "Xác nhận gửi" được active
- Option: "Dùng template có sẵn" (nếu có template email chuẩn cho loại thông báo này)

#### Path 2.3: AI sai (Failure path)

Người dùng phát hiện nội dung email sai trong HIL screen (tông sai, thông tin sai, grammar lỗi).
VD: "Chúng tôi rất tiếc thông báo..." (tông quá bi ai) hoặc sai số tiền.

**UI/UX:**
- **Editor inline:** Cho phép edit ngay nội dung email trong HIL screen (WYSIWYG hoặc markdown)
- Nút "Reset email" (quay lại draft AI)
- Nút "Soạn lại từ đầu" (xoá hết, user tự viết; hệ thống vẫn giữ merge field logic)
- Nút "Dùng template có sẵn" (chuyển sang một template khác)
- Nút "Thoát & lưu draft" (không gửi ngay, quay lại sau)
- Email chưa gửi cho đến khi user nhấn "Xác nhận gửi" lần cuối

#### Path 2.4: User sửa / mất niềm tin / thoát an toàn

Người dùng hoàn toàn không tin AI draft email.

**UI/UX:**
- "Soạn lại từ đầu" (xoá AI draft, user tự viết; hệ thống vẫn provide merge field helper)
- "Dùng template có sẵn" (chọn một email template đã được phê duyệt, có thể edit)
- "Thoát & lưu draft" (quay lại, draft được lưu, có thể xem lại sau hoặc tiếp tục ngày khác)
- Không mất dữ liệu danh sách người nhận (nếu từ UC1, danh sách vẫn được lưu)

---

## Path yếu nhất cần ưu tiên thiết kế

**UC2 — Path 2.3 & 2.2 (Low-confidence + Failure)**

Tại sao?
- **Path 2.3 (AI sai, email gửi sai nội dung hàng loạt):** Ảnh hưởng lớn nhất — email sai được gửi cho 487 người = ảnh hưởng uy tín, mối quan hệ với sinh viên, rủi ro PR.
- **Path 2.2 (AI không chắc, hallucinate thông tin):** Nếu không xử lý tốt (bằng placeholder + bắt buộc fill), user sẽ không biết phần nào sai.

**Cơ chế phòng thủ chính:** 
- **HIL là hàng rào cuối cùng** — phải thiết kế màn hình xác nhận kỹ lưỡng để user thực sự đọc & think, không nhấn "Gửi" theo quán tính.
- **Placeholder thay vì hallucinate** — nếu không chắc → hiển thị [CẦN ĐIỀN] rõ ràng
- **Editor inline để fix lỗi gần mục tiêu** — không phải quay lại soạn lại từ đầu

---

## 4. Evaluation Metrics

| Metric | Định nghĩa | Mục tiêu / Threshold | Cách đo |
|--------|------------|----------------------|---------|
| **NL-to-Query precision** | Tỉ lệ query dịch ra khớp intent người dùng (không cần refine) | ≥ 85% ở câu hỏi phổ biến | Ghi lại: query gốc + kết quả + có refine không; đánh giá thủ công 50 mẫu/tuần |
| **Retry rate** | % lần người dùng phải refine query ≥ 2 lần | ≤ 15% | Log từ hệ thống |
| **Email draft acceptance rate** | % email draft được gửi không chỉnh sửa nội dung | ≥ 60% (target) — **không phải càng cao càng tốt** — cần người dùng thực sự đọc kỹ | Log trước/sau edit; check edits.length == 0 |
| **HIL stop rate** | % lần người dùng dừng ở màn hình xác nhận, không gửi | Theo dõi theo thời gian; tăng đột biến = vấn đề data/draft quality | Log từ hệ thống; alert nếu > 20% |
| **Task time reduction** | Thời gian hoàn thành tác vụ so với quy trình thủ công (baseline) | Giảm ≥ 50% thời gian trung bình | Khảo sát + timed test với 5 user (trước/sau) |
| **Wrong send rate** | Tỉ lệ email gửi nhầm nội dung / nhầm người / sai danh sách trên tổng số email đã gửi | **Target: 0% trong pilot; chấp nhận tối đa < 0.1% ở vận hành thực tế, và 0 incident nghiêm trọng** | Incident log + manual spot-check (sample 5% email sent) |

**Ưu tiên:** Recall hơn Precision  cho UC2. Sai nhầm (gửi email sai) tốt hơn bỏ sót (chưa gửi được). HIL là hàng rào cuối cùng.

---

## 5. Failure Modes & Mitigation

| Failure Mode | Trigger | Tác động User | Phát hiện / Giảm thiểu |
|--------------|---------|---------------|------------------------|
| **NL-to-SQL sai ngữ nghĩa** | Query mơ hồ, schema phức tạp, tên cột không khớp | Người dùng tin dữ liệu sai → quyết định sai (VD: gửi email sai người) | **Phát hiện:** Hiển thị query đã dịch để user xác nhận; cảnh báo row count bất thường. **Giảm thiểu:** Read-only DB account; sanitize input |
| **AI hallucinate thông tin trong email** | LLM tự bịa số tiền, deadline, tên chương trình không có trong context | Email gửi thông tin sai hàng loạt → ảnh hưởng uy tín, tin cậy | **Phát hiện:** HIL screen preview email với dữ liệu thật. **Giảm thiểu:** Placeholder thay vì hallucinate; chỉ dùng data từ query result, không để LLM suy diễn tự do |
| **Gửi nhầm danh sách người nhận** | Query UC1 sai → danh sách sai; user không kiểm tra kỹ ở HIL | Email đến sai đối tượng (VD: gửi email "chưa đóng học phí" cho sinh viên đã đóng) → ảnh hưởng uy tín | **Phát hiện:** HIL screen hiển thị sample người nhận thật; warning nếu số lượng bất thường. **Giảm thiểu:** Không có "Gửi tất cả" 1 click; bắt buộc xem danh sách |
| **SQL injection qua NL input** | User nhập NL chứa câu lệnh SQL tiềm ẩn (VD: "show data; DROP TABLE..") | Rủi ro bảo mật, integrity của database | **Phát hiện:** WAF/input validation. **Giảm thiểu:** Sanitize input; parameterized queries; read-only DB account; không expose raw SQL cho user thường |
| **Over-trust — user không đọc HIL** | UX confirmation quá đơn giản → click qua nhanh theo quán tính | Mất hiệu quả của HIL → failure mode vẫn xảy ra | **Giảm thiểu:** Thiết kế HIL friction có chủ đích: hiển thị số người nhận lớn, preview email với data thật, *checkbox xác nhận đã đọc*, warning "Không thể thu hồi" |
| **Alexa Effect — data quality kém → AI càng kém** | Ít người dùng, ít correction signal, model không improve; loop going downwards | Adoption giảm, ROI âm | **Giảm thiểu:** Bắt đầu scope nhỏ (1 phòng ban, 1 loại query); thu correction data từ sớm; đánh giá thủ công định kỳ |

---

## 6. ROI Analysis (3 Scenarios)

**Giả định cơ sở:**
- **User base:** 2 phòng ban, ~5 nhân viên dùng thường xuyên
- **Baseline (hiện tại):** 
  - 1 truy vấn phức tạp = 30–60 phút (đợi IT hoặc tự làm Excel)
  - 1 email campaign hàng loạt cá nhân hoá = 2–4 giờ
- **After tool:** 
  - ~5 phút/query (bao gồm review + refine nếu cần)
  - ~15 phút/email campaign (bao gồm review HIL + fix nhỏ)
- **AI cost:** ~$0.02–0.05/query (LLM API); ~$10–30/tháng cho volume hiện tại

| Kịch bản | Mô tả | Kết quả ước tính |
|----------|-------|-----------------|
| **Best case** | Adoption cao (5 user, 10+ query/ngày), query accuracy ≥ 90%, staff tiết kiệm 3–4h/ngày/người | Tiết kiệm ~600h/năm (~75k USD labor @ ~75 USD/h); ROI dương sau **1 tháng**; data flywheel bắt đầu (feedback → fine-tune → accuracy ↑ → adoption ↑) |
| **Base case** | Adoption vừa (3 user, 3–5 query/ngày), accuracy 80%, cần refine thường xuyên (15% retry rate) | Tiết kiệm ~200h/năm (~25k USD); break-even sau **3 tháng**; useful nhưng không transformative; stable adoption |
| **Worst case** | Adoption thấp (1–2 user), accuracy < 70%, user mất tin và quay lại thủ công; high frustration | Không tiết kiệm thời gian thực; chi phí duy trì (infrastructure, support) > lợi ích; cân nhắc dừng sau **2 tháng** |

**Kill criteria:** 
- Nếu sau 2 tháng **retry rate > 40%** (query sai quá nhiều) → dừng UC1, review NL-to-SQL pipeline
- Nếu có **1 incident nghiêm trọng** (gửi sai đối tượng hàng loạt / sai nội dung nhạy cảm) **hoặc wrong send rate ≥ 0.1% trong 1 tháng** → tạm dừng UC2 để investigate

---

## 7. Mini AI Spec

| Hạng mục | Nội dung |
|----------|----------|
| **Luồng Use Case 1: NL Query** | Input: User nhập NL query text (VD: "Sinh viên K67 GPA < 2.0 học kỳ 1") → LLM dịch sang SQL → Function calling: Execute trên DB (read-only account) → Trả bảng kết quả → Output: HTML table + CSV download + nút kích hoạt UC2 / UC3 |
| **Luồng Use Case 2: Email Draft & HIL** | Input: Mục đích email (NL) + danh sách người nhận (từ UC1 hoặc manual upload CSV) → LLM draft email với merge fields {{tên}}, {{email}}, {{mã SV}}, {{custom field}} → HIL screen: preview + edit → User xác nhận (checkbox + warning) → Function calling: Gửi qua email service → Log status (sent, bounce, error) |
| **Luồng Use Case 3: Xuất báo cáo (V1.1+)** | Input: NL request (VD: "Báo cáo sinh viên chưa đóng học phí theo tình trạng") → LLM dịch → Execute query + aggregation → Tạo table + chart (bar/pie) → User export PDF hoặc email báo cáo |
| **Luồng Use Case 4: Danh sách tốt nghiệp (V1.1+)** | Input: "Danh sách tốt nghiệp kỳ tới?" → Query kết hợp students + transcripts + payments → Filter theo eligibility rules → Output: Bảng 3 cột (Tên, Mã, Tình trạng) + drill-down chi tiết → Export Excel |
| **Luồng Use Case 5: Email Campaign Analytics (V2)** | Input: "Báo cáo email campaigns tuần này" → Query email log table → Hiển thị campaign list (ngày, chủ đề, delivered, bounce rate) + chart trend → Drill-down bounce details |
| **Dữ liệu / Knowledge cần** | **Schema DB:** Tên bảng (students, payments, transcripts, emails), cột, quan hệ, ràng buộc → đưa vào system prompt của LLM. **Few-shot examples:** 5–8 ví dụ query phổ biến cho UC1+UC3. **Email templates:** 2–3 template email chuẩn theo loại. **Chart templates:** Config bar/pie chart cho UC3. **Eligibility rules:** Logic tốt nghiệp (encode trong system prompt hoặc rule engine). |
| **Model & Tools** | **LLM:** GPT-4o hoặc Claude 3.5 Sonnet (reasoning tốt cho NL-to-SQL + logic). **Function calling:** Safe DB query + email send + aggregation. **Database:** PostgreSQL/MySQL read-only connection. **Email service:** SMTP nội bộ hoặc SendGrid. **Visualization:** Charting library (Chart.js / D3.js) cho UC3. **Frontend:** React + TypeScript. **PDF export:** Library như PDFkit hoặc server-side (wkhtmltopdf). |
| **Guardrails & Policy** | DB account read-only — không UPDATE/DELETE/DROP; Sanitize NL input (strip SQL-like keywords, limit length); HIL bắt buộc trước mọi email send (UC2); Log đầy đủ: query, user, timestamp; email sent (recipient, status); chart/report generated; Rate limit: V1 max 500 người nhận/lần gửi; max 1000 row in table result; Cảnh báo user nếu data stale (timestamp cập nhật lần cuối) |
| **Không trong scope V1** | UC3, UC4, UC5 — focus hoàn toàn trên UC1 + UC2; Tự động gửi email không HIL; Truy cập dữ liệu tài chính nhạy cảm (balance, transaction details); Modify dữ liệu sinh viên (chỉ read); Advanced visualization / drill-down reports; Mobile app; Real-time collaboration / shared drafts |

---

## 8. Prototype Hackathon — Core Loop & Design Priorities

**Core loop (happy path):**
```
User inputs: "Sinh viên K67 chưa đóng học phí"
    ↓
AI translated query: "SELECT * FROM students WHERE khoa = 'K67' AND payment_status != 'completed' ..."
    ↓
User reviews query summary + row count: "27 sinh viên"
    ↓
User clicks "Xem danh sách" → preview table
    ↓
User confirms OR clicks "Sửa yêu cầu"
    ↓
User clicks "Soạn email cho danh sách này"
    ↓
AI drafts email + HIL screen
    ↓
User reviews + edits + confirms
    ↓
Email sent to 27 recipients; tracking log updated
```

**Design priorities (what to build first):**

1. **Error path UI trước happy path UI:**
   - Khi query sai: show query dịch, nút refine, warning row count
   - Khi AI không chắc: show interpretations, cho user chọn
   - Khi user không tin: show exit path (soạn lại, liên hệ IT, export), không có dead end
   
2. **HIL screen UC2 — "friction by design":**
   - Hiển thị danh sách người nhận thực tế (5–10 sample + "Xem tất cả")
   - Preview email với data sinh viên đầu tiên (tên, mã SV, số tiền)
   - Checkbox "Đã xem kỹ danh sách + nội dung" (không thể uncheck sau)
   - Warning: "Hành động này gửi email cho [số] người — không thể thu hồi"
   - Nút "Xác nhận gửi" chỉ active sau tick
   
3. **Scope V1 (Hackathon) — nhỏ gọn, tập trung UC1+UC2 ONLY:**
  - **UC1:** NL query → SQL dịch → bảng kết quả (students + payments schema)
  - **UC2:** Email draft + HIL + gửi hàng loạt
   - 3–5 loại query phổ biến nhất (VD: "K67 chưa đóng học phí", "K68 GPA < 2.0", "Chưa đăng ký môn học kỳ này")
   - 2–3 email template chuẩn (nhắc nhở học phí, thông báo sự kiện, kết quả học tập)
   - **Không** trong V1: UC3 (báo cáo), UC4 (tốt nghiệp), UC5 (email analytics), advanced visualization, mobile, permission system
   
   **Roadmap V1.1+ (sau hackathon):**
   - UC3: Xuất báo cáo + basic chart
   - UC4: Danh sách tốt nghiệp
   - UC5: Email campaign analytics (tracking)
   
4. **Eval từ sớm:**
   - Tối thiểu 5–10 user thực tế test trong 2 tuần cuối hackathon
   - Log mọi action (query, retry, email sent, stops at HIL, etc.)
   - Manual spot-check email được gửi (sample 5%)

---

## 9. Assignment Tracking

Chi tiết phân công: [**assignment-tracking.md**](assignment-tracking.md)

---