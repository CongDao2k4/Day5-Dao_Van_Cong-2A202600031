"""Database tools: registry, read-only guard, optional live PostgreSQL when env is set."""

from __future__ import annotations

import json
import os

import pytest

from tools.postgres_readonly import (
    DB_ID_ACADEMIC,
    DB_ID_CTSV,
    execute_sql,
    execute_sql_tool,
    get_db_list,
)

_HAS_ACADEMIC = bool(os.getenv('DATABASE_URL', '').strip())
_HAS_CTSV = bool(os.getenv('CTSV_DATABASE_URL', '').strip())


def test_registry_lists_two_databases() -> None:
    text = get_db_list.invoke({})
    assert DB_ID_ACADEMIC in text
    assert DB_ID_CTSV in text
    assert 'academic' in text.lower() or 'DATABASE_URL' in text
    assert 'CTSV' in text or 'ctsv' in text.lower()


@pytest.mark.skipif(not _HAS_ACADEMIC, reason='DATABASE_URL not set — skip live academic DB')
def test_academic_live_select() -> None:
    out = execute_sql(DB_ID_ACADEMIC, 'SELECT 1 AS one')
    assert out['ok'] is True
    assert out['db_id'] == DB_ID_ACADEMIC
    assert out['row_count'] == 1
    assert isinstance(out['rows'], list)
    assert out['rows'][0].get('one') == 1


@pytest.mark.skipif(not _HAS_CTSV, reason='CTSV_DATABASE_URL not set — skip live CTSV DB')
def test_ctsv_live_select() -> None:
    out = execute_sql(DB_ID_CTSV, 'SELECT COUNT(*)::bigint AS n FROM study_rooms')
    assert out['ok'] is True
    assert out['db_id'] == DB_ID_CTSV
    assert out['row_count'] == 1
    assert 'n' in out['rows'][0]


def test_rejects_non_select() -> None:
    out = execute_sql(DB_ID_ACADEMIC, 'DELETE FROM students WHERE 1=1')
    assert out['ok'] is False
    assert out['row_count'] == 0


@pytest.mark.skipif(not _HAS_ACADEMIC, reason='DATABASE_URL not set')
def test_alias_sis_db_maps_to_academic() -> None:
    out = execute_sql('sis_db', 'SELECT 1 AS x')
    assert out['ok'] is True
    assert out['db_id'] == DB_ID_ACADEMIC


@pytest.mark.skipif(not _HAS_ACADEMIC, reason='DATABASE_URL not set')
def test_execute_sql_tool_returns_json_string() -> None:
    raw = execute_sql_tool.invoke(
        {'db_id': DB_ID_ACADEMIC, 'sql': 'SELECT 1 AS y'}
    )
    data = json.loads(raw)
    assert 'row_count' in data
    assert 'rows' in data
