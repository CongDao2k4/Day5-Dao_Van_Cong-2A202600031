from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

from config import get_database_url


def check_connection() -> bool:
    """Return True if DATABASE_URL is set and PostgreSQL accepts a simple query."""
    url = get_database_url()
    if not url:
        return False
    try:
        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except Exception:
        return False


@contextmanager
def postgres_checkpointer() -> Iterator[PostgresSaver]:
    """Context-managed PostgresSaver. Caller should call ``setup()`` once before first checkpoint use."""
    url = get_database_url()
    if not url:
        raise ValueError("DATABASE_URL is not set")
    with PostgresSaver.from_conn_string(url) as saver:
        yield saver
