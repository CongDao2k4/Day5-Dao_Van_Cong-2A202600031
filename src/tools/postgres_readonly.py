"""PostgreSQL read-only tools: introspection, SELECT, and VinUni logical IDs for the agent."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import psycopg
from langchain_core.tools import tool
from psycopg.rows import dict_row

from config import get_ctsv_database_url, get_database_url
from telemetry.logger import logger

# --- Connection registry (technical keys used in SQL paths) ---

DATABASE_CONFIG: dict[str, dict[str, Any]] = {
    'academic': {
        'url_getter': get_database_url,
        'description': (
            'Academic records: students, GPA, tuition (env `DATABASE_URL`).'
        ),
        'env_var': 'DATABASE_URL',
    },
    'ctsv_booking': {
        'url_getter': get_ctsv_database_url,
        'description': (
            'CTSV: study room booking (`study_rooms`, `room_bookings`) — `CTSV_DATABASE_URL`.'
        ),
        'env_var': 'CTSV_DATABASE_URL',
    },
}

_MAX_ROWS = 1000
_STATEMENT_TIMEOUT_MS = 30_000

_DANGEROUS_SQL = re.compile(
    r'\b(DROP|DELETE|INSERT|UPDATE|TRUNCATE|ALTER|CREATE|GRANT|REVOKE)\b',
    re.IGNORECASE | re.DOTALL,
)

# --- Logical IDs exposed to the agent (SPEC) ---

DB_ID_ACADEMIC = 'vinuni_academic'
DB_ID_CTSV = 'vinuni_ctsv'

_DB_ALIASES: dict[str, str] = {
    'sis_db': DB_ID_ACADEMIC,
    'lms_db': DB_ID_CTSV,
}

_VINUNI_TO_TECH: dict[str, str] = {
    DB_ID_ACADEMIC: 'academic',
    DB_ID_CTSV: 'ctsv_booking',
}

DB_REGISTRY: list[dict[str, Any]] = [
    {
        'id': DB_ID_ACADEMIC,
        'description': DATABASE_CONFIG['academic']['description'],
        'dialect': 'postgresql',
        'keywords': [
            'student',
            'K67',
            'GPA',
            'tuition',
            'mssv',
            'invoice',
        ],
    },
    {
        'id': DB_ID_CTSV,
        'description': DATABASE_CONFIG['ctsv_booking']['description'],
        'dialect': 'postgresql',
        'keywords': [
            'booking',
            'study room',
            'CTSV',
            'study_rooms',
        ],
    },
]


def _canonical_logical_id(db_id: str) -> str:
    raw = (db_id or '').strip()
    return _DB_ALIASES.get(raw, raw)


def _tech_key_for_logical(cid: str) -> str | None:
    return _VINUNI_TO_TECH.get(cid)


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (bytes, memoryview)):
        return value.decode('utf-8', errors='replace')
    return value


def _validate_select_readonly(query: str) -> str | None:
    s = (query or '').strip()
    if not s:
        return 'Empty SQL.'
    low = s.lower()
    if not (low.startswith('select') or low.startswith('with')):
        return 'Only SELECT or WITH … SELECT (read-only) is allowed.'
    if _DANGEROUS_SQL.search(s):
        return 'Forbidden keyword in read-only mode.'
    if ';' in s.rstrip(';').rstrip():
        return 'Multiple statements are not allowed; use a single statement.'
    low2 = s.lower()
    forbidden_keywords = [
        'insert',
        'update',
        'delete',
        'drop',
        'truncate',
        'alter',
        'grant',
        'revoke',
        'create',
        'upsert',
    ]
    for word in forbidden_keywords:
        if re.search(rf'\b{word}\b', low2):
            return f"Forbidden in read-only mode: {word.upper()}."
    return None


def introspect_schema_markdown(url: str) -> str:
    """Build markdown for `public` tables and views (parameterized column lookup)."""
    lines: list[str] = ['### Schema (public)\n']
    try:
        with psycopg.connect(url, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type IN ('BASE TABLE', 'VIEW')
                    ORDER BY table_name
                    """
                )
                tables = cur.fetchall()
                if not tables:
                    lines.append('*(No tables or views in schema public.)*')
                    return '\n'.join(lines)

                for table_name, table_type in tables:
                    cur.execute(
                        """
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = %s
                        ORDER BY ordinal_position
                        """,
                        (table_name,),
                    )
                    cols = cur.fetchall()
                    kind = 'VIEW' if table_type == 'VIEW' else 'TABLE'
                    lines.append(f'#### {kind}: `{table_name}`')
                    for col_name, data_type, is_nullable in cols:
                        null = 'NULL' if is_nullable == 'YES' else 'NOT NULL'
                        lines.append(f'- `{col_name}` {data_type} {null}')
                    lines.append('')
    except Exception as e:
        return f'Error introspecting schema: {e!s}'
    return '\n'.join(lines).strip()


def introspect_for_db_type(db_type: str) -> str:
    if db_type not in DATABASE_CONFIG:
        return f"Error: unknown database key '{db_type}'."
    url = DATABASE_CONFIG[db_type]['url_getter']()
    if not url:
        ev = DATABASE_CONFIG[db_type]['env_var']
        return f'Error: {db_type} is not configured ({ev} missing).'
    body = introspect_schema_markdown(url)
    return f'--- Schema for `{db_type}` ---\n\n{body}'


def execute_select(db_type: str, query: str) -> dict[str, Any]:
    """Run a validated read-only query; returns JSON-serializable rows."""
    if db_type not in DATABASE_CONFIG:
        return {
            'ok': False,
            'error': f"Unknown database key '{db_type}'.",
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }

    err = _validate_select_readonly(query)
    if err:
        return {
            'ok': False,
            'error': err,
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }

    url = DATABASE_CONFIG[db_type]['url_getter']()
    if not url:
        ev = DATABASE_CONFIG[db_type]['env_var']
        return {
            'ok': False,
            'error': f'Environment variable {ev} is not set.',
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }

    try:
        with psycopg.connect(url, connect_timeout=15) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(f'SET statement_timeout = {_STATEMENT_TIMEOUT_MS}')
                cur.execute(query)
                rows = cur.fetchmany(_MAX_ROWS)
                safe = [_json_safe(dict(r)) for r in rows]
                return {
                    'ok': True,
                    'db_type': db_type,
                    'row_count': len(safe),
                    'rows': safe,
                    'read_only': True,
                    'hint': f'At most {_MAX_ROWS} rows; SELECT/WITH only.',
                }
    except Exception as e:
        return {
            'ok': False,
            'error': str(e).strip()[:2000],
            'rows': [],
            'row_count': 0,
            'db_type': db_type,
        }


def _rows_to_pipe_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '0 rows.'
    cols = list(rows[0].keys())
    header = ' | '.join(cols)
    sep = '-' * len(header)
    out = [header, sep]
    for r in rows:
        out.append(' | '.join(str(r.get(c)) for c in cols))
    return '\n'.join(out)


# --- Optional low-level tools (technical keys: academic / ctsv_booking) ---


@tool
def list_databases_tool() -> str:
    """List configured logical databases and their env vars."""
    info = 'Available databases (technical key → description):\n'
    for db_type, cfg in DATABASE_CONFIG.items():
        info += f"- `{db_type}`: {cfg['description']} (env: {cfg['env_var']})\n"
    info += (
        '\nThe ReAct agent uses logical IDs `vinuni_academic` / `vinuni_ctsv` '
        '(mapped to `academic` / `ctsv_booking`).\n'
    )
    return info


@tool
def get_schema_tool(db_type: str) -> str:
    """Return schema for a technical key: `academic` or `ctsv_booking`."""
    return introspect_for_db_type(db_type)


@tool
def execute_query_tool(db_type: str, query: str) -> str:
    """Run read-only SQL for a technical key; returns a plain-text table preview."""
    payload = execute_select(db_type, query)
    if not payload.get('ok'):
        return payload.get('error') or 'Unknown error.'

    rows: list[dict[str, Any]] = payload.get('rows') or []
    if not rows:
        return f'Result from {db_type}: 0 rows.'

    table = _rows_to_pipe_table(rows)
    n = payload.get('row_count', len(rows))
    hint = payload.get('hint', '')
    return f'--- Result from {db_type} ({n} rows) ---\n{hint}\n\n{table}'


# --- Agent-facing tools (VinUni logical IDs) ---


@tool
def get_db_list() -> str:
    """Step 1: choose DB — `vinuni_academic` vs `vinuni_ctsv`."""
    header = '## Registry — 2 PostgreSQL databases\n\n'
    entries = []
    for db in DB_REGISTRY:
        entry = (
            f'### ID: `{db["id"]}`\n'
            f'- **Description**: {db["description"]}\n'
            f'- **Dialect**: {db["dialect"]}\n'
            f'- **Keywords**: {", ".join(db["keywords"])}\n'
        )
        entries.append(entry)
    footer = (
        '\n---\n'
        '**Aliases:** `sis_db` → `vinuni_academic`, `lms_db` → `vinuni_ctsv`.\n'
        '**Technical keys** (for `list_databases_tool` / raw SQL helpers): '
        '`academic`, `ctsv_booking`.\n'
    )
    return header + '\n---\n'.join(entries) + footer


def get_db_schema(db_id: str) -> str:
    cid = _canonical_logical_id(db_id)
    tech = _tech_key_for_logical(cid)
    if not tech:
        return f"Error: invalid database ID '{db_id}'."
    inner = introspect_for_db_type(tech)
    if inner.startswith('Error:'):
        return inner
    return f'## Database `{cid}` (technical key: `{tech}`)\n\n{inner}'


def execute_sql(db_id: str, sql: str) -> dict[str, Any]:
    """Execute read-only SQL and return a dict for JSON tooling."""
    cid = _canonical_logical_id(db_id)
    tech = _tech_key_for_logical(cid)
    if not tech:
        return {
            'ok': False,
            'error': (
                f"Invalid database ID '{db_id}'. "
                f'Use {DB_ID_ACADEMIC} or {DB_ID_CTSV}.'
            ),
            'rows': [],
            'row_count': 0,
            'db_id': cid,
        }

    url = DATABASE_CONFIG[tech]['url_getter']()
    logger.log_event(
        'SQL_EXEC',
        {
            'db_id': cid,
            'db_type': tech,
            'sql_preview': (sql or '')[:500],
            'has_url': url is not None,
        },
    )

    payload = execute_select(tech, sql)
    out: dict[str, Any] = {**payload, 'db_id': cid}
    out.pop('db_type', None)
    return out


@tool
def get_db_schema_tool(db_id: str) -> str:
    """Return `public` schema for a logical `db_id` (`vinuni_*`)."""
    return get_db_schema(db_id)


@tool
def execute_sql_tool(db_id: str, sql: str) -> str:
    """Run read-only SQL; JSON string with rows and row_count."""
    payload = execute_sql(db_id, sql)
    return json.dumps(payload, ensure_ascii=False)


DB_AGENT_TOOLS = [get_db_list, get_db_schema_tool, execute_sql_tool]
