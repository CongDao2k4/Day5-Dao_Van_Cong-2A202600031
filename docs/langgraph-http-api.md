# Tài liệu HTTP API — LangGraph (chat & lịch sử phiên)

Contract chi tiết cũng có trong OpenAPI: `GET /docs` (Swagger), `GET /openapi.json`. Khi lệch, ưu tiên `/openapi.json` trên môi trường deploy.

---

## Mục đích

- **Chat:** gửi một lượt tin nhắn người dùng, chạy graph một vòng, nhận state đầu ra và giữ nhất quán theo **thread** (phiên hội thoại).
- **Lịch sử:** đọc các checkpoint của một thread để hiển thị timeline / debug (dữ liệu đến từ LangGraph `get_state_history`).
- **Meta:** biết graph đang chạy **agent** (LLM + tools) hay **stub** (demo không LLM) và loại checkpoint — để frontend parse `state` đúng.

---

## Địa chỉ cơ sở và OpenAPI

- **Base URL:** do môi trường triển khai quy định (ví dụ `http://localhost:8000` khi chạy `uvicorn` cục bộ). Mọi đường dẫn dưới đây là **relative** từ base URL.
- **OpenAPI / Swagger UI:** `GET /docs` — đối chiếu schema và thử request trong trình duyệt (khi server bật tài liệu tương tác).
- **OpenAPI JSON:** `GET /openapi.json` — sinh client types hoặc import Postman.

---

## Định dạng chung

- Các endpoint nhận/gửi JSON dùng **`application/json`** (trừ khi ghi chú khác).
- **Không có xác thực người dùng** trong phiên bản hiện tại: mọi client có thể gọi nếu tiếp cận được URL. Production nên bổ sung (reverse proxy, API key, v.v.).
- **CORS:** app **chưa** cấu hình CORS mặc định. Frontend origin khác (ví dụ Vite `localhost:5173`) cần proxy cùng origin hoặc `CORSMiddleware` phía server khi tích hợp.

---

## Luồng tích hợp gợi ý (frontend)

1. **`GET /meta`** — Lấy `graph_mode`, `agent_enabled`, `checkpoint_backend` trước khi render UI chat (stub vs agent khác cách hiển thị `state`).
2. **`GET /health`** (tuỳ chọn) — Probe DB cho banner “backend data”.
3. **`POST /chat`** — Gửi tin nhắn; nhận `thread_id`, `graph_mode`, `state`.
4. **`GET /threads/{thread_id}/history`** — Lịch sử checkpoint (time-travel / debug).

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
