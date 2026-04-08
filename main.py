"""Demo entrypoint: DB smoke, minimal LangGraph invoke, optional Gemini."""

import config  # noqa: F401 — load_dotenv side effect

from config import get_database_url, get_google_api_key
from graph import build_app
from postgres_checkpointer import check_connection, postgres_checkpointer


def main() -> None:
    print("=== LangGraph demo ===")

    db_url = get_database_url()
    if db_url:
        print(f"DATABASE_URL is set; connection OK: {check_connection()}")
    else:
        print("DATABASE_URL not set — graph runs in-memory (no Postgres checkpoint).")

    if db_url and check_connection():
        with postgres_checkpointer() as cp:
            cp.setup()
            app = build_app(checkpointer=cp)
            out = app.invoke(
                {"text": ""},
                config={"configurable": {"thread_id": "demo-thread-1"}},
            )
            print("Graph result (with PostgresSaver):", out)
    else:
        app = build_app()
        out = app.invoke({"text": ""})
        print("Graph result (no checkpointer):", out)

    if get_google_api_key():
        try:
            import httpx

            from gemini import get_chat_model

            model = get_chat_model()
            resp = model.invoke("Reply with a single short greeting word.")
            print("Gemini:", getattr(resp, "content", resp))
        except httpx.ConnectError as e:
            print("Gemini: network error — could not reach Google API (DNS or offline).")
            print(f"  ({type(e).__name__}: {e})")
            print("  Check: internet, DNS (e.g. getent hosts generativelanguage.googleapis.com), proxy env (HTTP_PROXY/HTTPS_PROXY).")
    else:
        print("GOOGLE_API_KEY not set — skip Gemini demo.")


if __name__ == "__main__":
    main()
