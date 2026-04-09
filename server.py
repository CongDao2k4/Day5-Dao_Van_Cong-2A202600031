"""ASGI entry: prepend ``src/`` to ``sys.path``, then expose FastAPI ``app``.

Run::

    uvicorn server:app --reload --host 0.0.0.0 --port 8000

No ``PYTHONPATH`` required (``src`` is added here).
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / 'src'
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from api.app import app

__all__ = ['app']
