"""Pydantic models for chat and history API (frontend contract + OpenAPI)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


GraphMode = Literal['agent', 'stub']
"""`agent` = Gemini ReAct + tools (`GOOGLE_API_KEY` set). `stub` = demo graph without LLM."""


class ChatRequest(BaseModel):
    """Một lượt hội thoại — input thống nhất cho cả agent và stub."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'message': 'Liệt kê sinh viên K67 GPA dưới 2.0 kỳ này',
                    'thread_id': '550e8400-e29b-41d4-a716-446655440000',
                },
                {'message': 'ping'},
            ]
        }
    )

    message: str = Field(
        ...,
        min_length=1,
        description=(
            'Nội dung người dùng (tiếng Việt hoặc Anh). '
            'Server map sang `messages[0]` (agent) hoặc `text` (stub).'
        ),
    )
    thread_id: str | None = Field(
        None,
        description='ID luồng hội thoại để checkpoint; bỏ trống → server tạo UUID mới.',
    )


class ChatResponse(BaseModel):
    """Output một lượt: luôn có `graph_mode` để frontend parse `state` đúng kiểu."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'thread_id': '550e8400-e29b-41d4-a716-446655440000',
                    'graph_mode': 'stub',
                    'state': {'text': 'xab'},
                },
                {
                    'thread_id': '550e8400-e29b-41d4-a716-446655440000',
                    'graph_mode': 'agent',
                    'state': {
                        'messages': [
                            {
                                'type': 'human',
                                'data': {
                                    'content': 'Chào',
                                    'type': 'human',
                                },
                            },
                            {
                                'type': 'ai',
                                'data': {
                                    'content': 'Xin chào! Tôi có thể giúp gì?',
                                    'type': 'ai',
                                    'tool_calls': [],
                                },
                            },
                        ]
                    },
                },
            ]
        }
    )

    thread_id: str = Field(description='Cùng giá trị gửi lên hoặc UUID do server tạo.')
    graph_mode: GraphMode = Field(
        description=(
            '`agent`: state có `messages` (danh sách LangChain message dict). '
            '`stub`: state có `text` (chuỗi demo).'
        ),
    )
    state: dict[str, Any] = Field(
        description=(
            'Giá trị state sau `invoke`. '
            'Khi `graph_mode=agent`, `messages` là mảng object `{type, data}` (JSON-safe). '
            'Khi `graph_mode=stub`, thường chỉ có `text`.'
        ),
    )


class HistoryCheckpointItem(BaseModel):
    """Một checkpoint trong lịch sử thread (giống LangGraph `StateSnapshot`, đã serialize)."""

    values: dict[str, Any] = Field(
        description='State tại checkpoint; `messages` đã chuyển sang dạng dict JSON-safe.',
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None
    checkpoint_id: str | None = None
    parent_checkpoint_id: str | None = None


class HistoryResponse(BaseModel):
    """Lịch sử checkpoint theo thread (thứ tự: newest first như iterator LangGraph)."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'thread_id': 't-1',
                    'checkpoints': [
                        {
                            'values': {'text': 'hiab'},
                            'metadata': {},
                            'created_at': None,
                            'checkpoint_id': 'ckpt-2',
                            'parent_checkpoint_id': 'ckpt-1',
                        }
                    ],
                }
            ]
        }
    )

    thread_id: str
    checkpoints: list[HistoryCheckpointItem]


class DbInstanceStatus(BaseModel):
    """Trạng thái kết nối tới một PostgreSQL (academic hoặc CTSV)."""

    configured: bool = Field(
        description='True nếu biến môi trường URL tương ứng đã set.',
    )
    reachable: bool | None = Field(
        None,
        description='True nếu SELECT 1 OK; False nếu có URL nhưng lỗi kết nối; null nếu không cấu hình.',
    )
    error: str | None = Field(
        None,
        description='Thông báo lỗi ngắn khi configured=true và reachable=false.',
    )


class DatabasesHealth(BaseModel):
    """Hai DB logic trong config (khác với mock `vinuni_*` trong agent tools)."""

    academic: DbInstanceStatus = Field(
        description='DATABASE_URL — học vụ; thường dùng chung cho LangGraph PostgresSaver.',
    )
    ctsv: DbInstanceStatus = Field(
        description='CTSV_DATABASE_URL — đặt phòng / CTSV.',
    )


class HealthResponse(BaseModel):
    """Liveness + probe DB."""

    status: Literal['ok'] = 'ok'
    databases: DatabasesHealth


class GraphMetaResponse(BaseModel):
    """Metadata để frontend biết cách bind UI (agent vs stub) mà không cần gọi chat."""

    graph_mode: GraphMode = Field(
        description='Trùng ý nghĩa với `graph_mode` trong `ChatResponse`.',
    )
    agent_enabled: bool = Field(
        description='True khi `GOOGLE_API_KEY` được set (ReAct + tools).',
    )
    checkpoint_backend: Literal['postgres', 'memory'] = Field(
        description='postgres nếu DATABASE_URL có và kết nối OK tại startup; ngược lại memory.',
    )
    openapi_docs_url: str = Field(default='/docs', description='Swagger UI.')
    openapi_json_url: str = Field(default='/openapi.json', description='OpenAPI schema JSON.')
