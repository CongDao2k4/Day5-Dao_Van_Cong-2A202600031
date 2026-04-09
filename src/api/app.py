"""FastAPI application: LangGraph chat, thread history, OpenAPI for frontend.

Run (repo root, venv active)::

    uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

- ``DATABASE_URL`` → ``PostgresSaver``; else ``MemorySaver``.
- See ``docs/langgraph-http-api.md`` and ``GET /meta`` for contract (``graph_mode``, ``state``).
"""

from __future__ import annotations

import sys
import uuid
from collections.abc import Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# Repo root so `graph` (project root) resolves when only `src` is on PYTHONPATH.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import psycopg  # noqa: E402

from langchain_core.messages import HumanMessage  # noqa: E402

from config import get_ctsv_database_url, get_database_url  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from graph import build_app, graph_uses_messages  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402
from langgraph.checkpoint.postgres import PostgresSaver  # noqa: E402
from langgraph.graph.state import CompiledStateGraph  # noqa: E402
from langgraph.types import StateSnapshot  # noqa: E402

from api.schemas import (  # noqa: E402
    ChatRequest,
    ChatResponse,
    DatabasesHealth,
    DbInstanceStatus,
    GraphMetaResponse,
    HealthResponse,
    HistoryCheckpointItem,
    HistoryResponse,
)
from api.state_serialization import serialize_graph_state  # noqa: E402


def _probe_postgres(url: str | None) -> DbInstanceStatus:
    """Return configuration and reachability for one connection string."""
    if not url:
        return DbInstanceStatus(configured=False, reachable=None)
    try:
        with psycopg.connect(url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
    except Exception as e:
        err = str(e).strip()
        return DbInstanceStatus(
            configured=True,
            reachable=False,
            error=err[:500] if err else 'connection failed',
        )
    return DbInstanceStatus(configured=True, reachable=True)


def _snapshot_to_item(snap: StateSnapshot) -> HistoryCheckpointItem:
    """Convert LangGraph StateSnapshot to JSON-serializable API model."""
    cc = (snap.config or {}).get('configurable') or {}
    pc = (snap.parent_config or {}).get('configurable') or {}
    cid = cc.get('checkpoint_id')
    pid = pc.get('checkpoint_id')
    md: dict[str, Any] = dict(snap.metadata) if snap.metadata else {}
    return HistoryCheckpointItem(
        values=serialize_graph_state(dict(snap.values)),
        metadata=md,
        created_at=str(snap.created_at) if snap.created_at is not None else None,
        checkpoint_id=str(cid) if cid is not None else None,
        parent_checkpoint_id=str(pid) if pid is not None else None,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open PostgresSaver for the process lifetime, or MemorySaver if no DATABASE_URL."""
    url = get_database_url()
    if url:
        cm = PostgresSaver.from_conn_string(url)
        checkpointer = cm.__enter__()
        try:
            checkpointer.setup()
        except Exception:
            cm.__exit__(*sys.exc_info())
            raise
        app.state.compiled = build_app(checkpointer)
        app.state._pg_cm = cm
        app.state.checkpoint_backend = 'postgres'
        try:
            yield
        finally:
            cm.__exit__(None, None, None)
    else:
        memory = MemorySaver()
        app.state.compiled = build_app(memory)
        app.state.checkpoint_backend = 'memory'
        yield


app = FastAPI(
    title='StudentOps API',
    description=(
        'Backend cho StudentOps AI: chat LangGraph, lịch sử checkpoint, health DB. '
        'Frontend: dùng `graph_mode` + `state` trong `ChatResponse` '
        '(xem `docs/langgraph-http-api.md`).'
    ),
    version='1.0.0',
    lifespan=lifespan,
    openapi_tags=[
        {
            'name': 'meta',
            'description': 'Cấu hình graph (agent vs stub) cho UI.',
        },
        {
            'name': 'chat',
            'description': 'Một lượt hội thoại; input/output contract trong schema.',
        },
        {
            'name': 'threads',
            'description': 'Lịch sử checkpoint theo `thread_id`.',
        },
        {
            'name': 'health',
            'description': 'Liveness và probe PostgreSQL (academic + CTSV).',
        },
    ],
)


def _get_graph() -> CompiledStateGraph:
    compiled = getattr(app.state, 'compiled', None)
    if compiled is None:
        raise HTTPException(status_code=503, detail='Graph not initialized')
    return compiled


def _graph_mode_label() -> str:
    return 'agent' if graph_uses_messages() else 'stub'


@app.get('/meta', response_model=GraphMetaResponse, tags=['meta'])
def graph_meta() -> GraphMetaResponse:
    """Metadata server: agent vs stub, checkpoint backend — gọi trước khi render chat UI."""
    cb = getattr(app.state, 'checkpoint_backend', 'memory')
    return GraphMetaResponse(
        graph_mode=_graph_mode_label(),  # type: ignore[arg-type]
        agent_enabled=graph_uses_messages(),
        checkpoint_backend=cb,  # type: ignore[arg-type]
    )


@app.get('/health', response_model=HealthResponse, tags=['health'])
def health() -> HealthResponse:
    """Liveness probe and status of configured PostgreSQL instances."""
    return HealthResponse(
        status='ok',
        databases=DatabasesHealth(
            academic=_probe_postgres(get_database_url()),
            ctsv=_probe_postgres(get_ctsv_database_url()),
        ),
    )


@app.post('/chat', response_model=ChatResponse, tags=['chat'])
def chat(body: ChatRequest) -> ChatResponse:
    """Một lượt graph: input `message` + optional `thread_id`; output `graph_mode` + `state` JSON-safe."""
    thread_id = body.thread_id or str(uuid.uuid4())
    cfg = {'configurable': {'thread_id': thread_id}}
    try:
        g = _get_graph()
        if graph_uses_messages():
            out = g.invoke(
                {'messages': [HumanMessage(content=body.message)]},
                cfg,
            )
        else:
            out = g.invoke({'text': body.message}, cfg)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    mode = _graph_mode_label()
    return ChatResponse(
        thread_id=thread_id,
        graph_mode=mode,  # type: ignore[arg-type]
        state=serialize_graph_state(dict(out)),
    )


@app.get('/threads/{thread_id}/history', response_model=HistoryResponse, tags=['threads'])
def thread_history(thread_id: str) -> HistoryResponse:
    """Danh sách checkpoint (newest first); `values` đã serialize `messages` giống `/chat`."""
    cfg = {'configurable': {'thread_id': thread_id}}
    try:
        snapshots: Iterator[StateSnapshot] = _get_graph().get_state_history(cfg)
        items = [_snapshot_to_item(s) for s in snapshots]
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return HistoryResponse(thread_id=thread_id, checkpoints=items)
