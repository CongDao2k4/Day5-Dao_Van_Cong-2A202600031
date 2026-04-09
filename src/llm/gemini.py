from langchain_google_genai import ChatGoogleGenerativeAI

from config import get_gemini_model, get_google_api_key


def get_chat_model() -> ChatGoogleGenerativeAI:
    key = get_google_api_key()
    if not key:
        raise ValueError('GOOGLE_API_KEY is not set')
    return ChatGoogleGenerativeAI(model=get_gemini_model(), temperature=0)
