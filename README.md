# C401 - D5

# Ngày 5 — Thiết kế sản phẩm AI cho sự không chắc chắn

> AI chạy được chưa phải product. Hôm nay học cách thiết kế cho uncertainty — khi AI có thể sai, UI phải xử lý thế nào?

---

## Tổng quan buổi học

```text
SÁNG — Lecture + Workshop                   CHIỀU — Lecture + Hackathon kickoff
┌──────────────────────────────┐            ┌──────────────────────────────┐
│ AI = probabilistic            │            │ Feedback loop + Data flywheel│
│ 3 trụ: Requirement · Eval · UX│     →      │ ROI 3 kịch bản               │
│ UX workshop (cá nhân)         │            │ Hackathon briefing           │
│ Canvas practice (nhóm)        │            │ Draft SPEC                   │
└──────────────────────────────┘            └──────────────────────────────┘
```

**Lecture** dạy framework: AI product khác phần mềm thường vì luôn có sai số. 3 trụ thiết kế: Requirement (precision/recall), Eval (metric + threshold), UX (4 paths khi AI đúng/sai/không chắc/user sửa). Canvas gộp tất cả vào 1 trang.

**Workshop + Practice** cho bạn thực hành trên sản phẩm AI thật (UX exercise) và bắt đầu thiết kế product AI của nhóm (Canvas practice + SPEC draft).

---

## Agenda

| Giờ | Hoạt động | Hình thức | Deliverable |
|-----|-----------|-----------|-------------|
| 9:00 | Opening — 3 cases thất bại + thesis "AI ≠ phần mềm thường" | Lecture | |
| 9:15 | Block 1: AI = probabilistic + Automation vs Augmentation | Lecture | |
| 9:45 | Block 2: 3 trụ — Requirement · Eval · UX | Mixed | |
| | — Requirement: lecture + Discord "tìm lỗi spec" | Discord (cá nhân, ~3 phút) | |
| | — Eval: lecture + Discord "precision hay recall?" | Discord (cá nhân, ~3 phút) | |
| | — **UX workshop:** phân tích sản phẩm AI thật | **Cá nhân** (40 phút) | **Sketch giấy + ghi chú 4 paths** |
| | — Debrief: kết nối 3 trụ | Lecture | |
| 11:10 | Break | | |
| 11:25 | Block 3: Canvas — Value / Trust / Feasibility + learning signal | Lecture | |
| 12:00 | Canvas practice — sketch Canvas cho project của nhóm + peer peek | Nhóm (25 phút) | |
| 13:00 | Nghỉ trưa | | |
| 14:00 | Block 4: Feedback loop + Data flywheel + Qual>Quant | Lecture | |
| 14:30 | Block 5: ROI 3 kịch bản | Lecture | |
| 15:00 | Q&A + Buffer | | |
| 15:30 | Break | | |
| 16:00 | **Hackathon briefing** + chia nhóm + chọn track + bắt đầu draft SPEC | Nhóm (3–5 người) | |
| **23h59** | **Deadline 08/04** | Nhóm | **Submit topic + SPEC draft** |

---

## Hoạt động chính

### 1. UX workshop — phân tích sản phẩm AI thật (40 phút, cá nhân)

Chọn 1 sản phẩm AI thật (MoMo / Vietnam Airlines / V-App), dùng thử, phân tích theo 4 paths, sketch cải thiện.

**Xem chi tiết:** [`02-ux-exercise.md`](02-ux-exercise.md)

**Output:** mỗi người nộp sketch giấy + ghi chú phân tích 4 paths. Đây là điểm cá nhân.

### 2. Canvas practice (25 phút, nhóm)

Sketch Canvas cho project của nhóm lên giấy A3 hoặc whiteboard. Peer peek: đi xem Canvas nhóm khác, ghi 1 feedback.

**Xem template:** [`03-canvas-template.md`](03-canvas-template.md)

### 3. SPEC draft (từ 16:00 + tối, nhóm)

Bắt đầu viết SPEC cho hackathon. Deadline: 23h59 08/04 Day 5.

SPEC gồm 6 phần: Canvas, User Stories 4 paths, Eval metrics, Failure modes, ROI, Mini AI spec.

**Template SPEC sẽ có trong repo hackathon:** [Day06-AI-Product-Hackathon](https://github.com/VinUni-AI20k/Day06-AI-Product-Hackathon)

---

## Deliverables

| # | Deliverable | Loại | Deadline | Nộp ở đâu |
|---|-------------|------|----------|------------|
| 1 | **Bài tập UX** — sketch giấy (as-is + to-be) + ghi chú phân tích 4 paths | Cá nhân | Cuối UX workshop (nộp tại lớp) + bản scan/ảnh trong repo | LMS |
| 2 | **SPEC draft** — topic + Canvas + hướng đi chính | Nhóm | 23:59 08/04/2026 | LMS |

---

## Cách tính điểm

Day 5 + Day 6 chấm chung = **100 điểm**.

| Hạng mục | Điểm | Loại | Khi nào |
|----------|------|------|---------|
| SPEC milestone | 25 | Nhóm + cá nhân | Draft 23h59 08/04 D5, final 23h59 09/04 |
| Prototype milestone | 15 | Nhóm + cá nhân | 23h59 09/04 |
| Demo Day | 25 | Nhóm | Present 16:00, nộp file 23h59 09/04 |
| **Bài tập UX** | **10** | **Cá nhân + bonus** | **UX workshop sáng D5** |
| Individual reflection | 25 | Cá nhân | 23h59 09/04 |
| **Tổng** | **100** | | |

### Bài tập UX (10 điểm + bonus)

| Tiêu chí | Điểm |
|----------|------|
| Phân tích 4 paths — đủ + nhận xét path yếu nhất | 4 |
| Sketch as-is + to-be rõ ràng, có breaking point | 4 |
| Nhận xét gap giữa marketing và thực tế sử dụng | 2 |
| **Bonus:** nhóm vote sketch hay nhất | +2 |

### Binary gate

| Tình huống | Hậu quả |
|-----------|---------|
| Không nộp SPEC draft trước 23:59 D5 | **-5 điểm** từ tổng SPEC (cả nhóm) |

---

## 4 hackathon tracks

| Track | Lĩnh vực | Gợi ý bài toán |
|-------|----------|----------------|
| **A** | VinFast | AI chatbot hỗ trợ mua xe/bảo dưỡng, phân tích review |
| **B** | Vinmec | AI triage, hỏi triệu chứng → gợi ý chuyên khoa |
| **C** | VinUni/VinSchool | AI tutor, trợ lý học tập, Q&A nội bộ |
| **D** | XanhSM | AI hỗ trợ tài xế/khách hàng, tối ưu trải nghiệm di chuyển |
| **E** | Tự chọn | Tự chọn domain, phải justify |

Nhóm 3–5 người, chia zone (~5 team/zone).

---

## Hướng dẫn nộp bài

**Deadline:** 23h59 08/04/2026 | **Nộp lên:** LMS | **Nộp link public GitHub repo**

Mỗi người tạo 1 **public repo** trên GitHub, nộp link repo lên LMS.

### Đặt tên repo

```
MaHocVien-HoTen-Day05
```

Ví dụ: `AI20K001-NguyenVanA-Day05`

### Cấu trúc repo

```
AI20K001-NguyenVanA-Day05/
│
├── canhan/
│   ├── ux-exercise/
│   │   ├── sketch.jpg hoặc sketch.pdf       ← Ảnh chụp/scan sketch giấy (as-is + to-be)
│   │   └── analysis.md                       ← Ghi chú phân tích 4 paths + gap marketing vs thực tế
│   │
│   └── extras/                               ← Tùy chọn — nộp thêm để lấy bonus
│       └── ...                               ← Reflection, ghi chú cá nhân, screenshot AI conversation,
│                                                research notes, hoặc bất kỳ output cá nhân nào khác
│
└── NhomXX-Room/                              ← Tên nhóm + phòng. VD: Nhom01-403
    └── spec-draft.md                         ← SPEC draft (file nhóm, mỗi người nộp giống nhau)
```

### Lưu ý

- Repo phải **public** — GV cần truy cập được để chấm
- **Folder `canhan/`** chứa bài cá nhân — đây là căn cứ chính cho điểm cá nhân UX exercise (10 điểm)
- **Folder `canhan/extras/`** không bắt buộc — nộp thêm các output cá nhân khác (reflection, research notes, prompt logs, screenshot...) sẽ được xét **bonus điểm** nếu nội dung có chất lượng
- **Folder `NhomXX-Room/`** chứa bài nhóm — tên folder phải khớp giữa các thành viên cùng nhóm
- File nhóm giống nhau giữa các thành viên là bình thường
- Sketch có thể là ảnh chụp giấy, scan, hoặc ảnh chụp whiteboard — miễn đọc được
- `analysis.md` viết bằng markdown, không cần format đẹp, cần đủ nội dung

---

## Ví dụ bài nộp tốt

### UX exercise — ví dụ analysis.md

```markdown
# UX exercise — MoMo Moni AI

## Sản phẩm: MoMo — Moni AI Assistant (phân loại chi tiêu)

## 4 paths

### 1. AI đúng
- User chi tiêu 50k tại Circle K → Moni gợi ý "Ăn uống"
- User thấy tag đúng, không cần làm gì thêm
- UI: hiện tag + icon category, không hỏi confirm

### 2. AI không chắc
- User chuyển tiền 200k cho bạn → Moni không tag hoặc tag "Khác"
- UI: không hiện gợi ý nào, user phải tự vào chỉnh
- Vấn đề: không có cơ chế "bạn muốn phân loại giao dịch này không?"

### 3. AI sai
- User mua sách trên Shopee → Moni tag "Mua sắm" thay vì "Học tập"
- User phát hiện khi xem báo cáo tháng
- Sửa: vào chi tiết giao dịch → đổi category → 3 bước
- Vấn đề: không rõ AI có học từ correction này không

### 4. User mất niềm tin
- Sau nhiều lần tag sai, user không tin báo cáo chi tiêu tự động nữa
- Không có option "tắt auto-tag" hoặc "tag thủ công trước"
- Không có fallback rõ ràng ngoài việc sửa từng giao dịch

## Path yếu nhất: Path 3 + 4
- Khi AI sai, recovery flow mất quá nhiều bước
- Không có feedback loop rõ — user sửa nhưng không biết AI có học không
- Không có exit/fallback cho user mất niềm tin

## Gap marketing vs thực tế
- Marketing: "Moni giúp quản lý chi tiêu thông minh"
- Thực tế: auto-tag chỉ đúng ~70% cho giao dịch phổ biến, các trường hợp edge case
  (chuyển tiền, mua online) thường bị tag sai hoặc không tag
- Gap lớn nhất: marketing không nói về khi AI sai — user kỳ vọng 100% chính xác

## Sketch
(Ảnh đính kèm: sketch.jpg)
- As-is: giao dịch → auto-tag → user thấy kết quả → nếu sai phải vào sửa thủ công
- To-be: giao dịch → auto-tag → nếu confidence thấp: hiện "Bạn muốn phân loại?"
  → user chọn → AI ghi nhận correction → hiện "Đã học, lần sau sẽ chính xác hơn"
```

### SPEC draft — ví dụ spec-draft.md (tối thiểu cần có)

```markdown
# SPEC draft — Nhom01-403

## Track: Vinmec

## Problem statement
Bệnh nhân đến Vinmec không biết nên khám chuyên khoa nào. Hiện tại hỏi lễ tân
hoặc tổng đài, mất 5-10 phút chờ, lễ tân phải tra danh mục thủ công. AI có thể
hỏi triệu chứng cơ bản và gợi ý chuyên khoa phù hợp.

## Canvas draft

| | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| Trả lời | Bệnh nhân mới, không biết chuyên khoa. Pain: chờ 10 phút, chọn sai khoa = khám lại. AI gợi ý top 3 khoa từ triệu chứng. | Nếu gợi ý sai khoa → bệnh nhân mất thời gian + tiền. Phải có option "gặp lễ tân" luôn hiện. | API call ~$0.005/lượt, latency <3s. Risk: triệu chứng mô tả mơ hồ, nhiều khoa overlap. |

**Auto hay aug?** Augmentation — AI gợi ý, bệnh nhân + lễ tân quyết định cuối cùng.

**Learning signal:** bệnh nhân chọn khoa nào sau gợi ý AI → so sánh với khoa thực tế khám → correction signal.

## Hướng đi chính
- Prototype: chatbot đơn giản hỏi 3-5 câu triệu chứng → gợi ý top 3 khoa + confidence
- Eval: precision trên top-3 suggestions ≥ 80%
- Main failure mode: triệu chứng chung chung ("đau bụng") → gợi ý quá rộng

## Phân công
- An: Canvas + failure modes
- Bình: User stories 4 paths
- Châu: Eval metrics + ROI
- Dũng: Prototype research + prompt test
```

---

## Tài liệu trong repo này

| File | Mô tả |
|------|-------|
| [`02-ux-exercise.md`](02-ux-exercise.md) | Đề bài UX workshop — hướng dẫn từng phần, tiêu chí nộp bài |
| [`03-canvas-template.md`](03-canvas-template.md) | Template AI Product Canvas — dùng cho Canvas practice |
| [`04-day5-cheatsheet.md`](04-day5-cheatsheet.md) | Tóm tắt 1 trang các framework từ lecture — tra cứu nhanh |
| [`05-reference-document.md`](05-reference-document.md) | Tài liệu tham khảo chi tiết — 14 frameworks, expert insights |

---

## Python / LangGraph (prototype) — cài đặt nhanh

1. **Python** 3.10+ (khuyến nghị 3.11+).
2. **Virtualenv** (từ thư mục gốc repo):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`

3. **Cài package**: `pip install -r requirements.txt`
4. **Biến môi trường**: `cp .env.example .env` rồi điền `DATABASE_URL` và/hoặc `GOOGLE_API_KEY` (tùy bạn muốn test phần nào).
5. **PostgreSQL** (khi dùng checkpoint): URI dạng `postgresql://user:pass@host:5432/dbname`. Lần chạy đầu với `PostgresSaver`, `main.py` gọi `setup()` để tạo bảng checkpoint.
6. **Thư mục `tools/`**: stub cho tool agent ↔ DB sau này; chưa có logic thật.

**Phiên bản gói:** `requirements.txt` căn theo **LangGraph 1.0.x** và **`langgraph-checkpoint-postgres`** (import `from langgraph.checkpoint.postgres import PostgresSaver`, `PostgresSaver.from_conn_string`, `.setup()`), cùng **`langchain-google-genai`** + model Gemini mặc định `gemini-2.5-flash` như tài liệu hiện tại của LangChain Google.

---

## Kiểm tra init (đảm bảo hoạt động đúng)

Làm từ **thư mục gốc** repo, **venv đã bật** (`source .venv/bin/activate`).

### Bước 1 — Import và phiên bản gói

```bash
python -c "from langgraph.checkpoint.postgres import PostgresSaver; from langchain_google_genai import ChatGoogleGenerativeAI; print('imports OK')"
```

- **Pass**: in `imports OK` và không traceback.
- **Lỗi** `No module named 'langgraph.checkpoint.postgres'`: cài thêm checkpoint Postgres — `pip install langgraph-checkpoint-postgres` (đã có trong `requirements.txt`; chạy lại `pip install -r requirements.txt`).

### Bước 2 — Chạy demo tích hợp (`main.py`)

```bash
python main.py
```

**Kịch bản A — Chưa cấu hình `.env` (hoặc trống key):**

- Thấy `DATABASE_URL not set` và/hoặc `GOOGLE_API_KEY not set`.
- **Bắt buộc pass**: dòng `Graph result (no checkpointer):` với `{'text': 'ab'}` (graph tối thiểu `node_a` → `node_b`).

**Kịch bản B — Có `DATABASE_URL` và Postgres chạy, DB tồn tại:**

- Thấy `connection OK: True`.
- Thấy `Graph result (with PostgresSaver):` cùng kết quả state (ví dụ `text` kết thúc bằng `ab`).
- **Nếu** `connection OK: False`: kiểm tra Postgres đã bật, user/password/database đúng, firewall/port `5432`.

**Kịch bản C — Có `GOOGLE_API_KEY` (Gemini):**

- Sau phần graph, thấy dòng `Gemini:` với nội dung trả lời ngắn.
- **Lỗi API key / quota**: xem thông báo từ thư viện; xác nhận key tại [Google AI Studio](https://aistudio.google.com/apikey).

### Bước 3 — Stub `tools/` (chỉ xác nhận package import được)

```bash
python -c "from tools.database import fetch_rows_stub"
```

- **Pass**: không in gì, thoát code 0.
- **Kịch bản kiểm tra “chưa implement”** (tùy chọn): `python -c "from tools.database import fetch_rows_stub; fetch_rows_stub('SELECT 1')"` → phải raise `NotImplementedError` (đúng thiết kế stub).

---

## Rời lớp Day 5, mỗi nhóm phải có

1. Track đã chọn (VinFast / Vinmec / VinUni-VinSchool / XanhSM / Open)
2. Problem statement 1 câu: "Ai gặp vấn đề gì, hiện giải thế nào, AI giúp được gì"
3. Phân công ai làm phần nào trong Canvas
4. SPEC draft submit trước 23h59 08/04

---

*Ngày 5 — VinUni A20 — AI Thực Chiến · 2026*
