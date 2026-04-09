# UX exercise — MoMo Moni AI

## Sản phẩm: MoMo — Trợ thủ AI Moni (Phân loại chi tiêu qua Chatbot)

---

## Phần 1: Khám phá (Marketing vs. Thực tế)

- **Marketing hứa hẹn**: AI Moni được giới thiệu là "trợ lý tài chính thông minh", có khả năng tự động nhận diện và phân loại mọi giao dịch qua hội thoại tự nhiên, giúp người dùng quản lý tài chính cá nhân một cách mượt mà và không tốn công sức.
- **Thực tế khi dùng**: Khi trải nghiệm tại mục *Quản lý chi tiêu -> Moni*, giao diện là một khung chat. Khi nhập liệu ví dụ: "ăn phở 50k", AI phản hồi ngay bằng một thẻ (card) ghi nhận và tự động gắn tag "Ăn uống". Tuy nhiên, sự "thông minh" đôi khi dừng lại ở việc gán nhãn cứng nhắc mà thiếu đi sự tương tác linh hoạt.

---

## Phần 2: Phân tích 4 Paths (Hành trình người dùng)

| Path | Mô tả User Story & Hành vi hệ thống |
|------|---------------------------------------|
| **1. Khi AI đúng** | **User story**: Nhập "Cafe 30k". <br> **Hành vi UI**: AI trả về Message Card hiển thị số tiền (-30.000đ), danh mục "Ăn uống", ngày giờ kèm animation tick xanh xác nhận. Cảm giác rất nhanh và tiện lợi. |
| **2. Khi AI không chắc** | **User story**: Nhập "đóng tiền 500k" (không rõ mục đích). <br> **Hành vi UI**: AI thường tự động gán vào "Chi tiêu khác" hoặc "Chưa phân loại". Hệ thống không đặt câu hỏi ngược lại để làm rõ (ví dụ: "Bạn đóng tiền điện hay tiền học?") |
| **3. Khi AI sai** | **User story**: Nhập "mua đồ chơi cho con 200k", AI lại gán nhầm vào "Sức khỏe". <br> **Sửa lỗi**: User phải bấm vào card -> Mở màn hình Edit -> Bấm vào Danh mục -> Cuộn tìm "Con cái" -> Bấm Lưu (Mất 3-4 thao tác). |
| **4. Khi user mất tin** | **Lối thoát (Exit)**: Bên cạnh thanh chat luôn có nút dấu cộng (+) để người dùng quay về form nhập liệu thủ công (Manual entry) truyền thống. Dễ tìm và đáng tin cậy. |

### Tự phân tích:
- **Path tốt nhất**: Path 1. Tốc độ nhận diện intent tốt, card hiển thị thông tin trực quan.
- **Path yếu nhất**: Path 3. Quy trình sửa lỗi quá dài (3-4 bước và chuyển trang), làm gãy mạch hội thoại và gây ức chế cho người dùng.
- **Kỳ vọng Marketing thực tế (Gap)**: Marketing nhấn mạnh vào sự thông minh của "trợ lý", nhưng thực tế AI của Moni vẫn đang hoạt động theo cơ chế "đoán mò" và gán nhãn một chiều thay vì có khả năng đối thoại để làm rõ ý định (Path 2).

---

## Phần 3: Sketch "Làm tốt hơn" (Cho Path 3 - AI Sai)

Tập trung vào giải quyết vấn đề gãy mạch trải nghiệm khi AI phân loại sai.

### 1. As-is (Hiện tại) - Chỗ gãy:
- User nhắn tin -> AI hiển thị kết quả sai danh mục.
- User phải nhấn vào thẻ để nhảy sang một màn hình chỉnh sửa khác hoàn toàn.
- **Vấn đề**: Flow quá dài, bắt user rời khỏi ngữ cảnh chat.

### 2. To-be (Đề xuất) - Inline Correction:
- **Cải tiến**: Ngay khi AI hiển thị thẻ kết quả, phía dưới sẽ xuất hiện các nút gợi ý nhanh (Quick-chips) nếu AI cảm thấy độ tin cậy không tuyệt đối.
- **Ví dụ**: Dưới thẻ "Ăn uống" (sai), hiện 3 nút: `[Dùng cho Con cái]` `[Sửa: Giáo dục]` `[Chọn khác...]`.
- **Kết quả**: User chỉ cần 1 lần chạm (tap) để sửa đúng danh mục ngay trong khung chat mà không cần chuyển trang.

---

*(Nộp bài: Đính kèm ảnh sketch giấy mô tả 2 màn hình As-is và To-be theo phân tích trên)*