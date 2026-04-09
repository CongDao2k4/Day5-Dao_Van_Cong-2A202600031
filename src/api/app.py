"""FastAPI application: LangGraph chat and thread history.

Run (repo root, venv active)::

    uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

Uses ``DATABASE_URL`` for ``PostgresSaver``; if unset, uses ``MemorySaver``.
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

from config import get_database_url  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from graph import build_app  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402
from langgraph.checkpoint.postgres import PostgresSaver  # noqa: E402
from langgraph.graph.state import CompiledStateGraph  # noqa: E402
from langgraph.types import StateSnapshot  # noqa: E402

from api.schemas import (  # noqa: E402
    ChatRequest,
    ChatResponse,
    HistoryCheckpointItem,
    HistoryResponse,
)


def _snapshot_to_item(snap: StateSnapshot) -> HistoryCheckpointItem:
    """Convert LangGraph StateSnapshot to JSON-serializable API model."""
    cc = (snap.config or {}).get('configurable') or {}
    pc = (snap.parent_config or {}).get('configurable') or {}
    cid = cc.get('checkpoint_id')
    pid = pc.get('checkpoint_id')
    md: dict[str, Any] = dict(snap.metadata) if snap.metadata else {}
    return HistoryCheckpointItem(
        values=dict(snap.values),
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
        try:
            yield
        finally:
            cm.__exit__(None, None, None)
    else:
        memory = MemorySaver()
        app.state.compiled = build_app(memory)
        yield


app = FastAPI(
    title='StudentOps LangGraph API',
    lifespan=lifespan,
)


def _get_graph() -> CompiledStateGraph:
    compiled = getattr(app.state, 'compiled', None)
    if compiled is None:
        raise HTTPException(status_code=503, detail='Graph not initialized')
    return compiled


@app.get('/health')
def health() -> dict[str, str]:
    """Liveness probe."""
    return {'status': 'ok'}


@app.post('/chat', response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    """Run one graph turn with optional persistent thread id."""
    thread_id = body.thread_id or str(uuid.uuid4())
    cfg = {'configurable': {'thread_id': thread_id}}
    try:
        out = _get_graph().invoke({'text': body.message}, cfg)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return ChatResponse(thread_id=thread_id, state=dict(out))


@app.get('/threads/{thread_id}/history', response_model=HistoryResponse)
def thread_history(thread_id: str) -> HistoryResponse:
    """List checkpoint snapshots for a thread (LangGraph `get_state_history`)."""
    cfg = {'configurable': {'thread_id': thread_id}}
    try:
        snapshots: Iterator[StateSnapshot] = _get_graph().get_state_history(cfg)
        items = [_snapshot_to_item(s) for s in snapshots]
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return HistoryResponse(thread_id=thread_id, checkpoints=items)
