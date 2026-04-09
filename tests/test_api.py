"""FastAPI chat + history smoke tests (MemorySaver when DATABASE_URL unset)."""

from __future__ import annotations

import sys

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Fresh app using in-memory checkpointer (no DATABASE_URL).

    ``setenv(...,'')`` prevents ``load_dotenv`` from repopulating real URLs
    (dotenv does not override existing keys).
    """
    monkeypatch.setenv('DATABASE_URL', '')
    monkeypatch.setenv('CTSV_DATABASE_URL', '')
    monkeypatch.setenv('GOOGLE_API_KEY', '')
    sys.modules.pop('api.app', None)
    sys.modules.pop('config', None)
    from api.app import app

    with TestClient(app) as tc:
        yield tc


def test_health(client: TestClient) -> None:
    r = client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'ok'
    dbs = data['databases']
    assert dbs['academic']['configured'] is False
    assert dbs['academic']['reachable'] is None
    assert dbs['ctsv']['configured'] is False
    assert dbs['ctsv']['reachable'] is None


def test_meta_stub_mode(client: TestClient) -> None:
    r = client.get('/meta')
    assert r.status_code == 200
    m = r.json()
    assert m['graph_mode'] == 'stub'
    assert m['agent_enabled'] is False
    assert m['checkpoint_backend'] == 'memory'
    assert m['openapi_docs_url'] == '/docs'


def test_chat_generates_thread_id(client: TestClient) -> None:
    r = client.post('/chat', json={'message': 'x'})
    assert r.status_code == 200
    data = r.json()
    assert 'thread_id' in data
    assert data['graph_mode'] == 'stub'
    assert data['state']['text'] == 'xab'


def test_chat_and_history_same_thread(client: TestClient) -> None:
    r1 = client.post('/chat', json={'message': 'hi', 'thread_id': 't-smoke'})
    assert r1.status_code == 200
    r2 = client.post('/chat', json={'message': 'again', 'thread_id': 't-smoke'})
    assert r2.status_code == 200
    hist = client.get('/threads/t-smoke/history')
    assert hist.status_code == 200
    body = hist.json()
    assert body['thread_id'] == 't-smoke'
    assert len(body['checkpoints']) >= 1
    assert all('values' in c for c in body['checkpoints'])
