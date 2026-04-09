"""Serialize LangGraph state for JSON / OpenAPI (messages are not JSON-serializable by default)."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import BaseMessage, messages_to_dict


def serialize_graph_state(values: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe copy of graph state (checkpoint values or invoke output)."""
    if not values:
        return {}
    out: dict[str, Any] = {}
    for key, val in values.items():
        if key == 'messages' and isinstance(val, list):
            if val and isinstance(val[0], BaseMessage):
                out[key] = messages_to_dict(val)
            else:
                out[key] = [_json_safe(x) for x in val]
        else:
            out[key] = _json_safe(val)
    return out


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, BaseMessage):
        return messages_to_dict([obj])[0]
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)
