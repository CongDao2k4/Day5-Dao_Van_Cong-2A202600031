#!/usr/bin/env python3
"""Minimal CLI: LangGraph invoke, optional Gemini smoke, Postgres checkpoint when configured."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure `src/` is importable when run as `uv run python scripts/demo.py`.
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import config  # noqa: F401 — load_dotenv side effect

from langchain_core.messages import HumanMessage

from checkpoints.postgres import check_connection, postgres_checkpointer
from config import get_database_url, get_google_api_key
from graph import build_app, graph_uses_messages
from llm.gemini import get_chat_model


def _gemini_quota_or_rate_limit(exc: BaseException) -> bool:
    """True if the failure is a Gemini 429 / quota / free-tier exhaustion."""
    chain: list[BaseException] = [exc]
    c = exc.__cause__
    while c is not None and len(chain) < 8:
        chain.append(c)
        c = c.__cause__
    for e in chain:
        name = type(e).__name__
        text = f'{name} {e}'.lower()
        if '429' in text or 'resource_exhausted' in text or 'quota' in text:
            return True
        if 'generativelanguage' in text and 'limit' in text:
            return True
    return False


def _print_quota_help() -> None:
    print()
    print('Gemini API: quota or rate limit (429 RESOURCE_EXHAUSTED).')
    print('  Free tier has tight per-day / per-minute limits per model.')
    print('  Options: wait (see error retry hint), enable billing, use another project/key,')
    print('  or set GEMINI_MODEL to another model. See:')
    print('  https://ai.google.dev/gemini-api/docs/rate-limits')
    print()


def _invoke_graph(
    app: Any,
    payload: dict[str, Any],
    cfg: dict[str, Any] | None,
) -> dict[str, Any] | None:
    try:
        return app.invoke(payload, config=cfg) if cfg is not None else app.invoke(payload)
    except Exception as e:
        if _gemini_quota_or_rate_limit(e):
            _print_quota_help()
            return None
        raise


def main() -> None:
    print('=== LangGraph demo ===')

    db_url = get_database_url()
    if db_url:
        print(f'DATABASE_URL is set; connection OK: {check_connection()}')
    else:
        print('DATABASE_URL not set — graph runs in-memory (no Postgres checkpoint).')

    out: dict[str, Any] | None = None

    if db_url and check_connection():
        with postgres_checkpointer() as cp:
            cp.setup()
            app = build_app(checkpointer=cp)
            cfg = {'configurable': {'thread_id': 'demo-thread-1'}}
            if graph_uses_messages():
                out = _invoke_graph(
                    app,
                    {'messages': [HumanMessage(content='ping')]},
                    cfg,
                )
            else:
                out = _invoke_graph(app, {'text': ''}, cfg)
            if out is not None:
                print('Graph result (with PostgresSaver):', out)
    else:
        app = build_app()
        if graph_uses_messages():
            out = _invoke_graph(app, {'messages': [HumanMessage(content='ping')]})
        else:
            out = _invoke_graph(app, {'text': ''})
        if out is not None:
            print('Graph result (no checkpointer):', out)

    if out is None:
        return

    # Agent mode already called Gemini inside the graph — do not send a second request.
    if graph_uses_messages():
        return

    if get_google_api_key():
        try:
            import httpx

            model = get_chat_model()
            resp = model.invoke('Reply with a single short greeting word.')
            print('Gemini (stub mode smoke):', getattr(resp, 'content', resp))
        except Exception as e:
            if _gemini_quota_or_rate_limit(e):
                _print_quota_help()
            elif isinstance(e, httpx.ConnectError):
                print('Gemini: network error — could not reach Google API (DNS or offline).')
                print(f'  ({type(e).__name__}: {e})')
                print(
                    '  Check: internet, DNS (e.g. getent hosts generativelanguage.googleapis.com), '
                    'proxy env (HTTP_PROXY/HTTPS_PROXY).'
                )
            else:
                raise
    else:
        print('GOOGLE_API_KEY not set — skip Gemini demo.')


if __name__ == '__main__':
    main()
