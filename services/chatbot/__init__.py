__all__ = ["build_chat_response"]


def build_chat_response(question: str):
    from .chat_service import build_chat_response as _build_chat_response

    return _build_chat_response(question)
