# Tài liệu HTTP API — LangGraph (chat & lịch sử phiên)

Contract chi tiết cũng có trong OpenAPI: `GET /docs` (Swagger), `GET /openapi.json`. Khi lệch, ưu tiên `/openapi.json` trên môi trường deploy.

---

## Mục đích

- **Chat:** gửi một lượt tin nhắn người dùng, chạy graph một vòng, nhận state đầu ra và giữ nhất quán theo **thread** (phiên hội thoại).
- **Lịch sử:** đọc các checkpoint của một thread để hiển thị timeline / debug (dữ liệu đến từ LangGraph `get_state_history`).
- **Meta:** biết graph đang chạy **agent** (LLM + tools) hay **stub** (demo không LLM) và loại checkpoint — để frontend parse `state` đúng.
- **HIL (email / hành động rủi ro):** xem mục **Human-in-the-loop (HIL)** trong tài liệu này — pattern khuyến nghị (LangGraph `interrupt` + Postgres) và cách frontend triển khai tạm thời với `/chat` hiện tại.

---

## Địa chỉ cơ sở và OpenAPI

- **Base URL:** do môi trường triển khai quy định (ví dụ `http://localhost:8000` khi chạy `uvicorn server:app` từ gốc repo — xem `server.py`). Mọi đường dẫn dưới đây là **relative** từ base URL.
- **OpenAPI / Swagger UI:** `GET /docs` — đối chiếu schema và thử request trong trình duyệt (khi server bật tài liệu tương tác).
- **OpenAPI JSON:** `GET /openapi.json` — sinh client types hoặc import Postman.

---

## Định dạng chung

- Các endpoint nhận/gửi JSON dùng **`application/json`** (trừ khi ghi chú khác).
- **Không có xác thực người dùng** trong phiên bản hiện tại: mọi client có thể gọi nếu tiếp cận được URL. Production nên bổ sung (reverse proxy, API key, v.v.).
- **CORS:** app **chưa** cấu hình CORS mặc định. Frontend origin khác (ví dụ Vite `localhost:5173`) cần proxy cùng origin hoặc `CORSMiddleware` phía server khi tích hợp.

---

## Ghi chú frontend — stub vs agent (quan trọng)

| `graph_mode` (`GET /meta` / `POST /chat`) | Ý nghĩa | UI chat nên hiểu thế nào |
|-------------------------------------------|---------|---------------------------|
| **`stub`** | Backend **không** load LLM (Gemini). Graph demo chỉ chạy hai bước cố định trên chuỗi `text`. | Phản hồi **không phải** AI: thường chỉ là **nối ký tự** (ví dụ gửi `"x"` → `state.text` kiểu `"xab"` — thêm `"a"` rồi `"b"`). **Đây là đúng thiết kế** khi thiếu key, không phải JSON mock hay bug API. |
| **`agent`** | Có **`GOOGLE_API_KEY`** trên **process** uvicorn / worker. | `state.messages` có hội thoại thật (ReAct + tools). Đây mới là “tin nhắn agent”. |

**Để bật agent thật:** cấu hình biến môi trường **`GOOGLE_API_KEY`** trên server (file `.env` cùng thư mục làm việc khi chạy app, hoặc biến trong PaaS), **restart** tiến trình FastAPI để nạp lại env. Kiểm tra: `GET /meta` → `graph_mode` = `"agent"`, `agent_enabled` = `true`.

Nếu vẫn thấy `stub` sau khi set key: xác nhận key không rỗng/không bị override, và server đọc đúng file env (xem `src/config.py` load `.env` từ gốc repo).

---

## Luồng tích hợp gợi ý (frontend)

1. **`GET /meta`** — Lấy `graph_mode`, `agent_enabled`, `checkpoint_backend` trước khi render UI chat (stub vs agent khác cách hiển thị `state`).
2. **`GET /health`** (tuỳ chọn) — Probe DB cho banner “backend data”.
3. **`POST /chat`** — Gửi tin nhắn; nhận `thread_id`, `graph_mode`, `state`.
4. **`GET /threads/{thread_id}/history`** — Lịch sử checkpoint (time-travel / debug).

---

## Human-in-the-loop (HIL) — khuyến nghị production

### Một luồng tối ưu (best practice LangGraph OSS)

Cho tác vụ **có rủi ro** (gửi email hàng loạt, giao dịch, xóa dữ liệu), **không** nên chỉ dựa vào prompt yêu cầu LLM “đừng gửi”. Pattern được framework hướng tới:

| Thành phần | Vai trò |
|------------|---------|
| **`interrupt()`** (trong node graph, trước khi gọi tool nguy hiểm) | Tạm dừng thực thi; đưa ra **yêu cầu phê duyệt** (ví dụ tên tool + `args`, mô tả/markdown preview). Human có thể **bỏ qua / trả lời / chỉnh sửa / chấp nhận** tùy cấu hình. |
| **Checkpointer bền** (khuyến nghị **Postgres** trong production) | **Durable execution**: thread không mất khi restart process; có thể **resume** đúng chỗ dừng. |
| **`configurable.thread_id`** (bắt buộc) | Xác định phiên; mọi lượt chat / resume dùng **cùng** `thread_id` cho một cuộc hội thoại chờ phê duyệt. |
| **`checkpoint_id`** (tùy chọn, khi cần) | Resume từ một checkpoint cụ thể (time travel / nhánh phê duyệt). |

Tài liệu framework nhấn mạnh: **human oversight** tại điểm dừng, **sửa state / quyết định**, rồi **tiếp tục** — phù hợp SPEC StudentOps (preview danh sách + nội dung + checkbox trước khi gửi).

**Vì sao không chọn “chỉ thêm endpoint REST `/email/confirm`” làm giải pháp duy nhất?** Endpoint tách vẫn hữu ích cho UI, nhưng **nguồn sự thật** nên là **graph + checkpoint**: tránh lệch giữa “đã draft ở đâu” và “confirm gửi ở đâu”, dễ audit và replay. Có thể **kết hợp**: interrupt bên trong graph + API mỏng map `resume` → `invoke`/`Command` với cùng `thread_id`.

### Trạng thái API **repo hiện tại**

- **`POST /chat`** chạy một lượt `invoke`; **chưa** trả về trạng thái **`interrupt`** / `__interrupt__` trong envelope JSON.
- HIL gửi mail (UC2) đang **hỗ trợ ở mức prompt** (agent được hướng dẫn không gọi `send_email` / `bulk_email_sender_tool` trừ khi user xác nhận trong chat) — **không thay thế** kiểm soát server-side như bảng trên.

Frontend vẫn nên **thiết kế UI HIL đầy đủ** (dưới) để khi backend bật `interrupt` + resume, chỉ cần nối vào cùng `thread_id` và payload resume (sẽ được bổ sung vào contract sau).

### Hướng dẫn triển khai Frontend (làm ngay — tương thích SPEC)

Cho luồng **soạn email / gửi hàng loạt**, UI nên tách rõ **ba pha** (dù HTTP hiện chỉ có `/chat`):

1. **Pha draft** — User mô tả yêu cầu; chat trả về trong `state.messages` (AI có thể gọi tool **draft** / mô tả danh sách). Hiển thị preview: sample người nhận, subject/body (merge field).
2. **Pha HIL (bắt buộc)** — Màn hình riêng: danh sách người nhận (hoặc số lượng), nội dung đã render, **checkbox** kiểu *“Đã xem kỹ danh sách và nội dung — không thể thu hồi”*, nút **Gửi** disabled cho đến khi tick.
3. **Pha xác nhận gửi** — Chỉ khi user tick + bấm gửi: gọi **`POST /chat`** lại với **cùng `thread_id`**, `message` là **câu xác nhận không mơ hồ** (product quy ước sẵn, ví dụ tiếng Việt có chứa cụm *“Xác nhận gửi email cho danh sách đã xem”* + có thể nhắc số người). Điều này **giảm** rủi ro gửi nhầm so với một câu chat thường; **không** bằng `interrupt()` nhưng khớp UX SPEC cho đến khi backend nâng cấp.

**Lưu ý:** Giữ **`thread_id`** cố định suốt draft → HIL → confirm để checkpoint (khi dùng Postgres) phản ánh đúng một phiên.

### Roadmap contract (khi backend tích hợp LangGraph interrupt)

- Response có thể bổ sung trường kiểu **`interrupted: true`** và payload phê duyệt (action + args + mô tả).
- Bước tiếp theo: cùng `thread_id`, body **`resume`** / **`Command`** (tuỳ bản API) — chi tiết sẽ vào OpenAPI khi implement.

---

## Endpoint tóm tắt

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/meta` | Cấu hình graph (agent/stub, checkpoint) |
| GET | `/health` | Liveness + trạng thái `DATABASE_URL` / `CTSV_DATABASE_URL` |
| POST | `/chat` | Một lượt hội thoại |
| GET | `/threads/{thread_id}/history` | Checkpoint theo thread |

---

## Thread ID (phiên hội thoại)

- **`thread_id`** xác định luồng checkpoint trên server (map `configurable.thread_id` của LangGraph).
- **Chat:** không gửi `thread_id` → server **tự sinh UUID** và trả trong response — client **lưu** và gửi lại cho các tin tiếp theo trong cùng cuộc hội thoại.
- **Lịch sử:** `thread_id` qua path parameter như endpoint bên dưới.

---

## Endpoint: `GET /meta`

| Thuộc tính | Giá trị |
|------------|---------|
| Phương thức & đường dẫn | `GET /meta` |
| Body | Không |

**Phản hồi thành công (HTTP 200):** JSON (`GraphMetaResponse`):

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `graph_mode` | `"agent"` \| `"stub"` | `agent` khi có `GOOGLE_API_KEY` (Gemini ReAct + tools). `stub` = graph demo không LLM. |
| `agent_enabled` | boolean | Cùng điều kiện với agent; tiện bind UI. |
| `checkpoint_backend` | `"postgres"` \| `"memory"` | Postgres khi `DATABASE_URL` có tại startup; không thì bộ nhớ trong process. |
| `openapi_docs_url` | string | `"/docs"` |
| `openapi_json_url` | string | `"/openapi.json"` |

---

## Endpoint: kiểm tra sống (health)

| Thuộc tính | Giá trị |
|------------|---------|
| Phương thức & đường dẫn | `GET /health` |
| Body | Không |

**Phản hồi thành công (HTTP 200):** JSON gồm:

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `status` | string | Luôn `"ok"` khi process trả lời (liveness). |
| `databases` | object | Hai khóa: `academic` và `ctsv` — mỗi khóa mô tả **một** instance PostgreSQL. |

**Một instance (ví dụ `databases.academic`):**

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `configured` | boolean | `true` nếu URL env được set. `academic` ↔ `DATABASE_URL`; `ctsv` ↔ `CTSV_DATABASE_URL`. |
| `reachable` | boolean hoặc `null` | `null` khi không cấu hình. `true` nếu `SELECT 1` OK. `false` nếu có URL nhưng lỗi kết nối. |
| `error` | string hoặc `null` | Khi `configured` và không `reachable`: lỗi rút gọn (~500 ký tự). |

---

## Endpoint: chat

| Thuộc tính | Giá trị |
|------------|---------|
| Phương thức & đường dẫn | `POST /chat` |
| Body (JSON) | Xem **ChatRequest** |

### ChatRequest (body)

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|--------|
| `message` | string | Có | Tối thiểu 1 ký tự. Map vào `messages[0]` (agent) hoặc `text` (stub). |
| `thread_id` | string hoặc `null` | Không | Phiên hội thoại; bỏ trống → server sinh UUID mới. |

### ChatResponse (HTTP 200)

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `thread_id` | string | Thread của lượt này (client hoặc server). |
| `graph_mode` | `"agent"` \| `"stub"` | **Dùng để chọn parser** cho `state`. |
| `state` | object | State sau `invoke`, **đã JSON-safe** (kể cả `messages` đã serialize). |

### `state` theo `graph_mode`

#### `graph_mode === "stub"`

- Thường chỉ có **`text`**: string (ví dụ demo nối ký tự).
- Ví dụ: `{ "text": "xab" }` nếu gửi `"message": "x"`.

#### `graph_mode === "agent"`

- Có **`messages`**: mảng message dạng LangChain dict (`messages_to_dict`).
- Mỗi phần tử dạng:

```json
{
  "type": "human",
  "data": {
    "content": "...",
    "type": "human",
    "tool_calls": [],
    "additional_kwargs": {},
    "response_metadata": {}
  }
}
```

- Với `type: "ai"`, `data.content` là nội dung hiển thị chính (có thể rỗng nếu chỉ `tool_calls`). Tool: `type: "tool"`, `data.content` là output tool.

**Gợi ý UI:** đọc `graph_mode` trước → `agent` thì render từ `state.messages` → `stub` thì `state.text`.

**Lỗi:**

- **HTTP 422:** validation (ví dụ `message` rỗng).
- **HTTP 503:** graph lỗi hoặc chưa init; `detail` là chuỗi lỗi.

---

## Endpoint: lịch sử checkpoint theo thread

| Thuộc tính | Giá trị |
|------------|---------|
| Phương thức & đường dẫn | `GET /threads/{thread_id}/history` |
| Path | `thread_id` — cùng ý nghĩa với chat. |
| Body | Không |

### HistoryResponse (HTTP 200)

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `thread_id` | string | Trùng path. |
| `checkpoints` | mảng | Snapshot; thứ tự **mới nhất trước** (`get_state_history`). |

### HistoryCheckpointItem (một phần tử trong `checkpoints`)

| Trường | Kiểu | Mô tả |
|--------|------|--------|
| `values` | object | State tại snapshot; **`messages` đã serialize** giống `/chat`. |
| `metadata` | object | Metadata LangGraph. |
| `created_at` | string hoặc `null` | Thời điểm snapshot. |
| `checkpoint_id` | string hoặc `null` | Id checkpoint. |
| `parent_checkpoint_id` | string hoặc `null` | Id checkpoint cha. |

**Lỗi:**

- **HTTP 503:** lỗi đọc lịch sử hoặc graph chưa init; `detail` mô tả lỗi.

---

## Hành vi lưu trữ phía server (ảnh hưởng frontend)

- **`DATABASE_URL`** có → checkpoint **Postgres** (bảng do LangGraph quản lý); `checkpoint_backend` trong `/meta` là `postgres`.
- **Không có `DATABASE_URL`** → **memory** trong process; **mất dữ liệu** sau restart.

Tính bền thread phụ thuộc triển khai backend, không phụ thuộc client.

---

## Biến môi trường ảnh hưởng hành vi

| Biến | Ảnh hưởng |
|------|-----------|
| `GOOGLE_API_KEY` | Có → `graph_mode=agent`, `state.messages`. Không → `stub`, `state.text`. |
| `DATABASE_URL` | Có → checkpoint Postgres + `checkpoint_backend=postgres`. Không → memory. |

---

## Phiên bản graph và contract

- **Stub:** state chủ yếu `text` (demo).
- **Agent:** state có `messages` (ReAct + tools). Hình dạng `state` / `values` có thể mở rộng theo graph; envelope HTTP (`thread_id`, `graph_mode`, `state`) giữ như schema Pydantic / OpenAPI.
