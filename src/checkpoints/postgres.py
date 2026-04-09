from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

from config import get_database_url


def check_postgres_url(url: str | None, *, connect_timeout: float = 5.0) -> bool:
    """Return True if *url* is non-empty and PostgreSQL accepts ``SELECT 1``."""
    if not (url or '').strip():
        return False
    try:
        with psycopg.connect(url.strip(), connect_timeout=connect_timeout) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
        return True
    except Exception:
        return False


def check_connection() -> bool:
    """True when ``DATABASE_URL`` is set and the server accepts a simple query."""
    return check_postgres_url(get_database_url())


@contextmanager
def postgres_checkpointer() -> Iterator[PostgresSaver]:
    """Context-managed PostgresSaver. Caller should call ``setup()`` once before first checkpoint use."""
    url = get_database_url()
    if not url:
        raise ValueError('DATABASE_URL is not set')
    with PostgresSaver.from_conn_string(url) as saver:
        yield saver
