"""LangGraph application: stub demo (no API key) or Gemini ReAct agent with tools + telemetry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict

from config import get_gemini_model, get_google_api_key
from llm.gemini import get_chat_model
from telemetry.logger import logger
from telemetry.metrics import llm_performance_tracker
from tools.postgres_readonly import DB_AGENT_TOOLS
from tools.email import EMAIL_TOOLS
from tools.email_draft import email_draft_tool
from tools.export_data_tool import export_data

_PACKAGE = Path(__file__).resolve().parents[1]
_PROMPT_PATH = _PACKAGE / 'prompts' / 'react_agent_system.txt'

AGENT_TOOLS = [
    *EMAIL_TOOLS,
    email_draft_tool,
    *DB_AGENT_TOOLS,
    export_data,
]


def graph_uses_messages() -> bool:
    """True when `build_app` compiles the ReAct agent (needs `GOOGLE_API_KEY`)."""
    return bool(get_google_api_key())


def _load_system_prompt() -> str:
    if _PROMPT_PATH.is_file():
        return _PROMPT_PATH.read_text(encoding='utf-8').strip()
    return (
        'You are StudentOps: help with student data, email, and exports using your tools.'
    )


def _telemetry_post_model(state: dict[str, Any]) -> dict[str, Any]:
    """Log model turns: token usage when present, tool calls, and performance metrics."""
    msgs: list[Any] = state.get('messages') or []
    for m in reversed(msgs):
        if not isinstance(m, AIMessage):
            continue
        tool_names: list[str] = []
        if m.tool_calls:
            for tc in m.tool_calls:
                name = tc.get('name') if isinstance(tc, dict) else getattr(tc, 'name', None)
                if name:
                    tool_names.append(str(name))
        if tool_names:
            logger.log_event('AGENT_TOOL_CALL', {'tools': tool_names})

        usage: dict[str, Any] = {}
        um = getattr(m, 'usage_metadata', None)
        if isinstance(um, dict):
            usage = um
        else:
            rm = getattr(m, 'response_metadata', None) or {}
            if isinstance(rm, dict):
                u = rm.get('usage_metadata')
                if isinstance(u, dict):
                    usage = u

        if usage:
            inp = int(
                usage.get('input_tokens')
                or usage.get('input_token_count')
                or usage.get('prompt_tokens')
                or 0,
            )
            out = int(
                usage.get('output_tokens')
                or usage.get('output_token_count')
                or usage.get('candidates_tokens')
                or usage.get('completion_tokens')
                or 0,
            )
            total = int(usage.get('total_tokens') or (inp + out))
            model_name = str(
                (getattr(m, 'response_metadata', None) or {}).get('model_name')
                or get_gemini_model(),
            )
            llm_performance_tracker.track_request(
                'google_genai',
                model_name,
                {
                    'input_tokens': inp,
                    'output_tokens': out,
                    'total_tokens': total,
                },
                latency_ms=0,
            )
        logger.log_event(
            'AGENT_MODEL_TURN',
            {
                'content_preview': (m.content or '')[:240]
                if isinstance(m.content, str)
                else str(type(m.content)),
            },
        )
        break
    return {}


def _build_react_agent(checkpointer: Any = None) -> Any:
    model = get_chat_model()
    prompt = _load_system_prompt()
    logger.log_event(
        'GRAPH_BUILD',
        {
            'mode': 'react',
            'model': get_gemini_model(),
            'tools': [t.name for t in AGENT_TOOLS],
        },
    )
    return create_react_agent(
        model,
        AGENT_TOOLS,
        prompt=prompt,
        checkpointer=checkpointer,
        post_model_hook=_telemetry_post_model,
        name='vinuni_ops_react',
    )


class StubState(TypedDict):
    text: str


def _node_a(state: StubState) -> dict[str, str]:
    return {'text': state['text'] + 'a'}


def _node_b(state: StubState) -> dict[str, str]:
    return {'text': state['text'] + 'b'}


def _build_stub_graph(checkpointer: Any = None) -> Any:
    logger.log_event('GRAPH_BUILD', {'mode': 'stub_ab', 'tools': []})
    graph = StateGraph(StubState)
    graph.add_node('node_a', _node_a)
    graph.add_node('node_b', _node_b)
    graph.add_edge(START, 'node_a')
    graph.add_edge('node_a', 'node_b')
    if checkpointer is not None:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


def build_app(checkpointer: Any = None) -> Any:
    """Compile LangGraph: ReAct + tools when `GOOGLE_API_KEY` is set, else linear stub."""
    if graph_uses_messages():
        return _build_react_agent(checkpointer)
    return _build_stub_graph(checkpointer)


def get_compiled_graph_for_cli() -> Any:
    """In-memory graph for LangGraph CLI / ``langgraph.json`` (no Postgres)."""
    from langgraph.checkpoint.memory import MemorySaver

    return build_app(MemorySaver())
