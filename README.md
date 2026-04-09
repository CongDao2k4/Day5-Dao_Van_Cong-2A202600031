# C401 — D5 · StudentOps (backend)

Backend FastAPI + LangGraph cho prototype **StudentOps** (VinUni / VinSchool).

| Artefact | Vị trí |
|----------|--------|
| Báo cáo nhóm | [`group_report/`](group_report/) |
| SPEC nhóm (draft) | [`group_report/spec-draft-vinuni-vinschool.md`](group_report/spec-draft-vinuni-vinschool.md) |
| SPEC nhóm (final) | [`group_report/spec-final-vinuni-vinschool.md`](group_report/spec-final-vinuni-vinschool.md) |
| Báo cáo cá nhân | [`individual_reports/`](individual_reports/) |
| HTTP API (contract, Swagger `/docs`) | [`docs/langgraph-http-api.md`](docs/langgraph-http-api.md) |
| **Frontend** | [Day6-C401-D5-FE](https://github.com/RhythmGC/Day6-C401-D5-FE.git) |

---

## Thành viên nhóm

**Tên nhóm:** C401 - D5

Báo cáo cá nhân

| Thành viên | Mã HV | Thư mục báo cáo |
|-------------|-------|-----------------|
| Đào Phước Thịnh | 2A202600029 | `individual_reports/2A202600029_DaoPhuocThinh/` |
| Nguyễn Tri Nhân | 2A202600224 | `individual_reports/2A202600224-NguyenTriNhan/` |
| Trần Xuân Trường | 2A202600321 | `individual_reports/2A202600321-TranXuanTruong/` |
| Hồ Sỹ Minh Hà | 2A202600060 | `individual_reports/HoSyMinhHa-2A202600060/` |
| Nông Nguyễn Thành | 2A202600250 | `individual_reports/2A202600250-NongNguyenThanh/` |
| Đào Văn Công | 2A202600031 | `individual_reports/2A202600031-DaoVanCong/` |

---

## Bố cục repo (tóm tắt)

```text
C401-D5-Day-05-06/
├── database/                    # SQL DDL + mock data (không trùng schema với Python — cần khớp nếu agent gọi SQL)
├── docs/
│   └── langgraph-http-api.md    # contract HTTP API / Swagger
├── group_report/                # báo cáo & SPEC nhóm
├── individual_reports/          # báo cáo cá nhân (theo thư mục từng HV)
├── scripts/
│   └── demo.py                  # CLI demo (graph + checkpoint)
├── src/
│   ├── api/                     # FastAPI: app.py, schemas, state JSON
│   ├── graph/                   # build_app: ReAct agent hoặc stub
│   ├── tools/                   # postgres_readonly (2 DB), email, export
│   ├── llm/                     # Gemini factory
│   ├── checkpoints/             # Postgres probe + PostgresSaver
│   ├── prompts/                 # react_agent_system.txt, v1/planner, v1/sql_generator, …
│   ├── templates/               # HTML mẫu email / export
│   ├── telemetry/               # log / metrics (nếu bật)
│   └── config.py
├── tests/
├── server.py                    # ASGI: thêm src/ → import api.app:app
├── pyproject.toml
└── requirements.txt
```

---

## StudentOps — luồng hoạt động (prototype trong repo)

```text
                    ┌─────────────────────────────────────────────────────────┐
  Frontend / CLI    │  FastAPI (`src/api/app.py`)                              │
       │            │  POST /chat  GET /meta  GET /health  GET /threads/…/history │
       └──────────► │         │                                                │
                    │         ▼                                                │
                    │  `build_app(checkpointer)`  ←  PostgresSaver hoặc MemorySaver
                    │         │                                                │
                    │         ├── GOOGLE_API_KEY có  → ReAct agent (Gemini)     │
                    │         │                    + tools: DB PostgreSQL (2),│
                    │         │                      email, export (`src/graph/`)│
                    │         │                                                │
                    │         └── GOOGLE_API_KEY không → graph stub (demo `text`)│
                    │                    │                                     │
                    │                    ▼                                     │
                    │  State trả về được serialize JSON (`messages` hoặc `text`) │
                    └─────────────────────────────────────────────────────────┘
```

- **Checkpoint:** nếu có `DATABASE_URL` và kết nối OK lúc startup, LangGraph dùng **Postgres** để lưu thread; không thì **bộ nhớ trong process** (mất khi restart).
- **Hai DB nghiệp vụ:** `vinuni_academic` / `vinuni_ctsv` trong `src/tools/postgres_readonly.py` (key kỹ thuật `academic` / `ctsv_booking`). Cùng hai URI `DATABASE_URL` / `CTSV_DATABASE_URL` như probe `/health` và checkpoint (có thể trùng server, khác database).
- **API:** mô tả trong file HTTP API (bảng Artefact phía trên) và `GET /docs` khi server chạy.

---

## Chạy local (dev)

**Yêu cầu:** Python **3.12+** (theo `pyproject.toml`).

### Cài dependency (khuyến nghị [uv](https://github.com/astral-sh/uv))

```bash
cd /path/to/C401-D5-Day-05-06
uv sync
uv sync --extra dev    # pytest — chỉ cần khi chạy test
```

Có thể dùng `pip install -e .` hoặc `pip install -r requirements.txt` nếu không dùng uv (bản `requirements.txt` ở gốc repo là tối thiểu).

### Biến môi trường

```bash
cp .env.example .env
```

Điền tùy chọn:

| Biến | Tác dụng |
|------|----------|
| `GOOGLE_API_KEY` | Bật **agent** ReAct + Gemini + tools; không có → **stub** demo |
| `DATABASE_URL` | Postgres cho **checkpoint** thread + truy vấn agent DB học vụ (`academic`) |
| `CTSV_DATABASE_URL` | Truy vấn agent CTSV (`ctsv_booking`) + **probe** trong `/health` |
| `GEMINI_MODEL` | Mặc định `gemini-2.5-flash` |
| `SMTP_*` | Gửi email thật qua tool (khi agent gọi) — xem `src/config.py` |

### `PYTHONPATH` (bắt buộc khi chạy từ gốc repo)

Package ứng dụng nằm dưới `src/` (`config`, `api`, `tools`, …). Từ thư mục gốc, set:

```bash
export PYTHONPATH=src
```

(Windows CMD: `set PYTHONPATH=src` — PowerShell: `$env:PYTHONPATH="src"`)

Không set sẽ lỗi `ModuleNotFoundError: config` / `api`. Thư mục `tests/` tự thêm `src` qua `conftest.py`.

### Chạy demo CLI (`scripts/demo.py`)

```bash
uv run python scripts/demo.py
```

(`scripts/demo.py` tự thêm `src/` vào `sys.path`; không cần `PYTHONPATH`.)

- Không `DATABASE_URL`: in-memory checkpoint; stub → state kiểu `{'text': 'ab'}`.
- Có `DATABASE_URL` + Postgres: `PostgresSaver` + `setup()`.
- Có `GOOGLE_API_KEY` + **agent**: một lượt `invoke` với `HumanMessage("ping")` (một request Gemini). Lỗi **429 / quota** được in gợi ý thay vì traceback dài.
- Có `GOOGLE_API_KEY` + **stub** (không agent): thêm một smoke `Gemini` ngắn (để test API khi graph không gọi LLM).
- Free tier Gemini có giới hạn request/ngày — xem [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

### Chạy HTTP API (cho frontend)

```bash
uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

File **`server.py`** ở gốc repo chỉ thêm `src/` vào `sys.path` rồi import `api` — **không cần** `export PYTHONPATH=src` khi dùng lệnh này.

Nếu vẫn muốn gọi trực tiếp module package: `PYTHONPATH=src uv run uvicorn api.app:app ...`

- Swagger: **http://127.0.0.1:8000/docs**
- Gợi ý flow: `GET /meta` → `POST /chat` → `GET /threads/{id}/history` (cùng file HTTP API ở bảng Artefact).

### PostgreSQL (checkpoint)

URI dạng `postgresql://user:pass@host:5432/dbname`. Lần đầu LangGraph tạo bảng checkpoint qua `PostgresSaver.setup()` trong lifespan.

Script SQL mẫu cho dữ liệu nghiệp vụ (tuỳ nhóm): thư mục `database/` (`setup_academic.sql`, …). Cần schema khớp nếu agent gọi `execute_sql_tool`; không bắt buộc chỉ để chạy graph **stub** (không LLM).

---

## Kiểm tra nhanh

### Import stack

```bash
PYTHONPATH=src uv run python -c "from langgraph.checkpoint.postgres import PostgresSaver; from langchain_google_genai import ChatGoogleGenerativeAI; print('imports OK')"
```

### Chạy test (pytest)

Cần `uv sync --extra dev` (hoặc cài `pytest` tương đương). Từ gốc repo:

```bash
uv run pytest tests/ -q
```

### Smoke API (server đã chạy)

```bash
curl -s http://127.0.0.1:8000/meta | jq .
curl -s -X POST http://127.0.0.1:8000/chat -H 'Content-Type: application/json' -d '{"message":"hi"}' | jq .
```
