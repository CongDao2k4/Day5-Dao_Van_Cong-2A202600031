"""Pydantic models for chat and history API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """User message for one graph turn."""

    message: str = Field(..., min_length=1, description='User text passed to graph state `text`.')
    thread_id: str | None = Field(
        None,
        description='Conversation thread; if omitted, server generates a UUID.',
    )


class ChatResponse(BaseModel):
    """Graph output for one turn."""

    thread_id: str
    state: dict[str, Any]


class HistoryCheckpointItem(BaseModel):
    """One snapshot from `get_state_history` (JSON-safe)."""

    values: dict[str, Any]
    metadata: dict[str, Any]
    created_at: str | None = None
    checkpoint_id: str | None = None
    parent_checkpoint_id: str | None = None


class HistoryResponse(BaseModel):
    """Ordered history for a thread (newest first per LangGraph iterator)."""

    thread_id: str
    checkpoints: list[HistoryCheckpointItem]
