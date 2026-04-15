from .context_builders import build_context, build_direct_context
from .llm_service import ask_ollama
from .suggestion_service import get_contextual_suggestions


def build_chat_response(question: str) -> dict:
    clean_question = question.strip()
    if not clean_question:
        return {"reply": "Vui lòng nhập câu hỏi.", "data": None}

    structured_data = build_direct_context(clean_question)
    if structured_data:
        return {
            "reply": structured_data.get("title", ""),
            "data": structured_data,
            "suggestions": get_contextual_suggestions(clean_question, structured_data),
        }

    context = build_context(clean_question)
    answer = ask_ollama(clean_question, context)
    return {
        "reply": answer,
        "data": None,
        "suggestions": get_contextual_suggestions(clean_question, None),
    }
