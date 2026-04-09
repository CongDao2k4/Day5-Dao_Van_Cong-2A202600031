"""Mock two logical DBs for StudentOps (SPEC: VinUni Đào Tạo + CTSV) — read-only simulated SQL."""

from __future__ import annotations

import json
import re

from langchain_core.tools import tool

from telemetry.logger import logger

# Canonical ids (SPEC: two databases — academic học vụ vs CTSV truyền thông)
DB_ID_ACADEMIC = 'vinuni_academic'
DB_ID_CTSV = 'vinuni_ctsv'

# Legacy aliases → canonical (prompts / few-shots may still reference old names)
_DB_ALIASES: dict[str, str] = {
    'sis_db': DB_ID_ACADEMIC,
    'lms_db': DB_ID_CTSV,
}


def _canonical_db_id(db_id: str) -> str:
    raw = (db_id or '').strip()
    return _DB_ALIASES.get(raw, raw)


class DatabaseManager:
    def execute(self, db_id: str, sql: str) -> object: ...


db_manager = DatabaseManager()

DB_REGISTRY = [
    {
        'id': DB_ID_ACADEMIC,
        'description': (
            'VinUni — Phòng Đào Tạo (học vụ): sinh viên, học phí/thanh toán, GPA, '
            'đăng ký môn, điểm. Dùng cho UC1: "K67 chưa đóng học phí", "GPA < 2.0", v.v.'
        ),
        'dialect': 'postgresql',
        'keywords': [
            'sinh viên',
            'K67',
            'K68',
            'GPA',
            'học phí',
            'tuition',
            'đăng ký môn',
            'tín chỉ',
            'billing',
            'transcript',
        ],
    },
    {
        'id': DB_ID_CTSV,
        'description': (
            'VinUni — Phòng Cộng Tác Sinh Viên (CTSV): truyền thông, chiến dịch email '
            '(mock log), thông báo. Dùng cho UC2 follow-up / "campaign tuần này" (mock).'
        ),
        'dialect': 'postgresql',
        'keywords': [
            'email campaign',
            'CTSV',
            'thông báo',
            'gửi mail',
            'bounce',
            'delivered',
        ],
    },
]


@tool
def get_db_list() -> str:
    """Bước 1 khi cần dữ liệu từ DB: liệt kê `vinuni_academic` vs `vinuni_ctsv` và mô tả.

    Gọi **trước** khi chọn `db_id` cho `execute_sql_tool` nếu chưa chắc nên dùng DB nào.
    """
    header = '## REGISTRY — 2 DATABASE (VinUni / SPEC hackathon)\n\n'
    entries = []
    for db in DB_REGISTRY:
        entry = (
            f'### ID: `{db["id"]}`\n'
            f'- **Mô tả**: {db["description"]}\n'
            f'- **Dialect**: {db["dialect"]}\n'
            f'- **Gợi ý từ khóa**: {", ".join(db["keywords"])}\n'
        )
        entries.append(entry)
    legacy = (
        '\n---\n**Alias (cũ, map tự động):** `sis_db` → `vinuni_academic`, '
        '`lms_db` → `vinuni_ctsv`.\n'
    )
    return header + '\n---\n'.join(entries) + legacy


def _schema_academic() -> str:
    return """
### DATABASE: `vinuni_academic` (Phòng Đào Tạo — học vụ)
Read-only mô phỏng PostgreSQL. Bảng chính cho UC1 (SPEC: students + payments).

#### TABLE: students
- student_id (BIGINT, PK)
- mssv (TEXT): Mã số sinh viên (VD: 2A202600029)
- full_name (TEXT)
- email (TEXT)
- cohort (TEXT): Khóa (VD: K67, K68)
- major (TEXT)
- status (TEXT): Enrolled | Graduated | Withdrawn | On-Leave
- gpa_term (FLOAT): GPA kỳ gần nhất (0.0–4.0)
- credits_registered (INT): Tín chỉ đã đăng ký kỳ hiện tại
- credits_earned (INT): Tín chỉ tích lũy

#### TABLE: payments (học phí / billing theo SPEC)
- payment_id (BIGINT, PK)
- student_id (BIGINT, FK → students.student_id)
- term_code (TEXT): VD 2026-S1
- amount_due_vnd (BIGINT): Số phải đóng (VND)
- amount_paid_vnd (BIGINT): Đã đóng
- payment_status (TEXT): pending | partial | paid | overdue

#### TABLE: grades
- student_id (BIGINT, FK)
- course_id (BIGINT)
- grade (FLOAT): 0.0–4.0
- semester (TEXT): YYYY-S1 / YYYY-S2

Quan hệ: payments.student_id = students.student_id; grades.student_id = students.student_id.
"""


def _schema_ctsv() -> str:
    return """
### DATABASE: `vinuni_ctsv` (CTSV — truyền thông, mock)
Read-only mô phỏng. Dùng cho lịch sử chiến dịch email (UC2 / UC5 roadmap).

#### TABLE: email_campaigns
- campaign_id (BIGINT, PK)
- subject (TEXT)
- sent_at (DATE)
- recipient_count (INT)
- delivered_count (INT)
- bounce_count (INT)
- notes (TEXT)

#### TABLE: notification_templates (gợi ý nội dung — mock)
- template_id (BIGINT, PK)
- name (TEXT)
- category (TEXT): tuition | event | academic
"""


MOCK_SCHEMAS: dict[str, str] = {
    DB_ID_ACADEMIC: _schema_academic(),
    DB_ID_CTSV: _schema_ctsv(),
}


def get_db_schema(db_id: str) -> str:
    """Returns a semantically enriched schema summary for NL→SQL."""
    cid = _canonical_db_id(db_id)
    return MOCK_SCHEMAS.get(cid, f"Error: Database ID '{db_id}' not found.")


_DANGEROUS_SQL = re.compile(
    r"\b(DROP|DELETE|INSERT|UPDATE|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE | re.DOTALL,
)


def _validate_readonly_sql(sql: str) -> str | None:
    """Return error message if SQL is not safe for read-only mock; else None."""
    s = (sql or '').strip()
    if not s:
        return 'SQL rỗng.'
    if not re.match(r'^\s*SELECT\b', s, re.IGNORECASE):
        return 'Chỉ cho phép SELECT (read-only, theo SPEC).'
    if _DANGEROUS_SQL.search(s):
        return 'Câu lệnh chứa từ khóa không được phép (read-only).'
    if ';' in s.rstrip(';').rstrip():
        return 'Không hỗ trợ nhiều câu lệnh (;). Một SELECT duy nhất.'
    return None


def _rows_academic() -> list[dict[str, object]]:
    """Mock rows: cover SPEC examples (K67 học phí, GPA)."""
    return [
        {
            'student_id': 101,
            'mssv': '2A202600029',
            'full_name': 'Dao Phuoc Thinh',
            'email': 'thinh.dp@vinuni.edu.vn',
            'cohort': 'K67',
            'major': 'AI Engineering',
            'status': 'Enrolled',
            'gpa_term': 1.85,
            'credits_registered': 18,
            'credits_earned': 90,
            'term_code': '2026-S1',
            'amount_due_vnd': 35_000_000,
            'amount_paid_vnd': 10_000_000,
            'payment_status': 'partial',
        },
        {
            'student_id': 102,
            'mssv': '2A202600224',
            'full_name': 'Nguyen Tri Nhan',
            'email': 'nhan.nt@vinuni.edu.vn',
            'cohort': 'K67',
            'major': 'Computer Science',
            'status': 'Enrolled',
            'gpa_term': 3.65,
            'credits_registered': 21,
            'credits_earned': 75,
            'term_code': '2026-S1',
            'amount_due_vnd': 0,
            'amount_paid_vnd': 35_000_000,
            'payment_status': 'paid',
        },
        {
            'student_id': 103,
            'mssv': '2A202600321',
            'full_name': 'Tran Xuan Truong',
            'email': 'truong.tx@vinuni.edu.vn',
            'cohort': 'K68',
            'major': 'AI Engineering',
            'status': 'Enrolled',
            'gpa_term': 1.72,
            'credits_registered': 0,
            'credits_earned': 28,
            'term_code': '2026-S1',
            'amount_due_vnd': 42_000_000,
            'amount_paid_vnd': 0,
            'payment_status': 'overdue',
        },
        {
            'student_id': 104,
            'mssv': '2A202600250',
            'full_name': 'Nong Nguyen Thanh',
            'email': 'thanh.nn@vinuni.edu.vn',
            'cohort': 'K67',
            'major': 'Data Science',
            'status': 'Enrolled',
            'gpa_term': 3.10,
            'credits_registered': 15,
            'credits_earned': 60,
            'term_code': '2026-S1',
            'amount_due_vnd': 12_000_000,
            'amount_paid_vnd': 0,
            'payment_status': 'pending',
        },
    ]


def _rows_ctsv() -> list[dict[str, object]]:
    return [
        {
            'campaign_id': 1,
            'subject': 'Nhắc nhở học phí kỳ 2026-S1',
            'sent_at': '2026-04-01',
            'recipient_count': 487,
            'delivered_count': 480,
            'bounce_count': 7,
            'notes': 'Mock — theo UC5 roadmap',
        },
        {
            'campaign_id': 2,
            'subject': 'Thông báo sự kiệm CTSV tuần 15',
            'sent_at': '2026-04-08',
            'recipient_count': 1200,
            'delivered_count': 1188,
            'bounce_count': 12,
            'notes': 'Mock',
        },
    ]


def execute_sql(db_id: str, sql: str) -> dict[str, object]:
    """Simulate read-only SQL; returns structured payload for the agent + UI."""
    cid = _canonical_db_id(db_id)
    err = _validate_readonly_sql(sql)
    logger.log_event(
        'MOCK_SQL_EXEC',
        {'db_id': cid, 'sql_preview': (sql or '')[:500], 'error': err},
    )
    if err:
        return {'ok': False, 'error': err, 'rows': [], 'row_count': 0, 'db_id': cid}

    if cid == DB_ID_ACADEMIC:
        rows = _rows_academic()
    elif cid == DB_ID_CTSV:
        rows = _rows_ctsv()
    else:
        return {
            'ok': False,
            'error': f"Unknown db_id '{db_id}'. Use {DB_ID_ACADEMIC} or {DB_ID_CTSV}.",
            'rows': [],
            'row_count': 0,
            'db_id': cid,
        }

    # Mock engine: optional trivial filters for demo (SPEC happy path)
    sql_lower = (sql or '').lower()
    filtered = list(rows)
    if 'k67' in sql_lower or "cohort = 'k67'" in sql_lower.replace(' ', ''):
        filtered = [r for r in filtered if str(r.get('cohort', '')).upper() == 'K67']
    if 'gpa' in sql_lower and ('<' in sql or 'under' in sql_lower):
        filtered = [r for r in filtered if float(r.get('gpa_term', 99)) < 2.0]
    if 'overdue' in sql_lower or 'payment_status' in sql_lower:
        if 'overdue' in sql_lower:
            filtered = [r for r in filtered if r.get('payment_status') == 'overdue']
        elif 'pending' in sql_lower:
            filtered = [r for r in filtered if r.get('payment_status') == 'pending']
        elif 'partial' in sql_lower:
            filtered = [r for r in filtered if r.get('payment_status') == 'partial']

    return {
        'ok': True,
        'db_id': cid,
        'row_count': len(filtered),
        'rows': filtered,
        'read_only': True,
        'hint': 'Dữ liệu mock cho demo; kiểm tra lại ý định trước khi dùng cho UC2.',
    }


@tool
def get_db_schema_tool(db_id: str) -> str:
    """Bước 2: lấy schema (bảng/cột) cho `db_id` trước khi viết SQL.

    Bắt buộc gọi trước `execute_sql_tool` lần đầu với DB đó (trừ khi vừa gọi trong cùng lượt và đã nhớ).
    """
    return get_db_schema(db_id)


@tool
def execute_sql_tool(db_id: str, sql: str) -> str:
    """Bước 3 — **nguồn sự thật duy nhất** cho số liệu: chạy SELECT read-only, trả JSON `row_count` + `rows`.

    **Cấm** trả lời người dùng về MSSV, tên, GPA, học phí, số lượng sinh viên nếu chưa có kết quả từ tool này
    (hoặc tool khác trả đúng dữ liệu nghiệp vụ). Mọi con số trong câu trả lời phải khớp JSON `rows`/`row_count`.
    """
    payload = execute_sql(db_id, sql)
    return json.dumps(payload, ensure_ascii=False)


DB_AGENT_TOOLS = [get_db_list, get_db_schema_tool, execute_sql_tool]
