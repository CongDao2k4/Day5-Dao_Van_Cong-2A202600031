import os

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str | None:
    url = os.getenv("DATABASE_URL")
    return url.strip() if url else None


def get_google_api_key() -> str | None:
    key = os.getenv("GOOGLE_API_KEY")
    return key.strip() if key else None


def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
