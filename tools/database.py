"""Placeholder functions for future agent ↔ PostgreSQL tools. No runtime behavior yet."""


def get_connection():
    """Return a live DB connection for agent tools (not implemented)."""
    raise NotImplementedError


def fetch_rows_stub(sql: str, params: tuple | None = None) -> None:
    """Placeholder for a parameterized read helper bound as an agent tool."""
    raise NotImplementedError


def execute_stub(sql: str, params: tuple | None = None) -> None:
    """Placeholder for writes / migrations called from tooling (use with care in agents)."""
    raise NotImplementedError
