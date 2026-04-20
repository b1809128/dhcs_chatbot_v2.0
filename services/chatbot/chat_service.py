from .context_builders import build_context, build_direct_context
from .llm_service import ask_ollama
from .rag_service import build_rag_context
from .suggestion_service import get_contextual_suggestions
from .utils import format_context_data


STRUCTURED_RESPONSE_TYPES = {"table", "list", "pdf_document"}


def build_chat_response(question: str) -> dict:
    clean_question = question.strip()
    if not clean_question:
        return {
            "reply": "Vui lòng nhập câu hỏi.",
            "data": None,
            "suggestions": [],
            "references": [],
            "source": "structured",
        }

    structured_data = build_direct_context(clean_question)
    if structured_data and structured_data.get("type") in STRUCTURED_RESPONSE_TYPES:
        return {
            "reply": structured_data.get("title", ""),
            "data": structured_data,
            "suggestions": get_contextual_suggestions(clean_question, structured_data),
            "references": [],
            "source": "structured",
        }

    if structured_data:
        context, references = build_rag_context(
            clean_question,
            preferred_context=structured_data,
        )
        if not context:
            context = format_context_data(structured_data)
        suggestions = get_contextual_suggestions(clean_question, structured_data)
    else:
        context, references = build_rag_context(clean_question)
        if not context:
            context = build_context(clean_question)
        suggestions = get_contextual_suggestions(clean_question, None)

    answer = ask_ollama(clean_question, context)
    return {
        "reply": answer,
        "data": None,
        "suggestions": suggestions,
        "references": references if context else [],
        "source": "ollama",
    }
