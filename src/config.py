import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_REPO_ROOT / '.env')

TlsMode = Literal['starttls', 'ssl']


def get_database_url() -> str | None:
    url = os.getenv("DATABASE_URL")
    return url.strip() if url else None


def get_google_api_key() -> str | None:
    key = os.getenv("GOOGLE_API_KEY")
    return key.strip() if key else None


def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()


def get_smtp_host() -> str | None:
    v = os.getenv('SMTP_HOST')
    return v.strip() if v else None


def get_smtp_port() -> str | None:
    v = os.getenv('SMTP_PORT')
    return v.strip() if v else None


def get_smtp_user() -> str | None:
    v = os.getenv('SMTP_USER')
    return v.strip() if v else None


def get_smtp_password() -> str | None:
    v = os.getenv('SMTP_PASSWORD')
    return v.strip() if v else None


def get_smtp_from() -> str | None:
    v = os.getenv('SMTP_FROM')
    return v.strip() if v else None


def get_smtp_tls_mode() -> TlsMode:
    raw = (os.getenv('SMTP_TLS_MODE') or 'starttls').strip().lower()
    if raw in ('ssl', 'smtps', 'implicit'):
        return 'ssl'
    return 'starttls'
