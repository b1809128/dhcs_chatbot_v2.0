from .context_builders import build_context, build_direct_context
from .keywords import ADMISSION_KEYWORDS
from .llm_service import ask_ollama
from .rag_service import build_rag_context
from .suggestion_service import get_contextual_suggestions
from .utils import contains_any, format_context_data


STRUCTURED_RESPONSE_TYPES = {
    "table",
    "list",
    "pdf_document",
    "document_file",
    "document_collection",
}

RAG_FIRST_ADMISSION_KEYWORDS = [
    "tuyển sinh",
    "tuyen sinh",
    "văn bằng 2",
    "văn bằng hai",
    "van bang 2",
    "van bang hai",
    "vb2",
    "điều kiện",
    "phương thức",
    "xét tuyển",
    "chỉ tiêu",
    "ngành tuyển sinh",
    "cấu trúc đề thi",
    "ngưỡng đầu vào",
    "timeline",
    "lộ trình",
    "checklist",
    "tóm tắt",
]

STRUCTURED_ACTION_KEYWORDS = [
    "văn bằng 2",
    "văn bằng hai",
    "van bang 2",
    "van bang hai",
    "vb2",
    "css",
    "vb2ca",
    "bài thi",
    "ca1",
    "ca2",
    "ca3",
    "ca4",
    "thông tư",
    "luật",
    "nghị định",
    "công văn",
    "đơn",
    "pdf",
    "word",
    "tải",
    "mở",
    "xem file",
    "đủ điều kiện",
    "du dieu kien",
    "đăng ký được",
    "dang ky duoc",
    "có đăng ký",
    "co dang ky",
    "liên thông",
    "lien thong",
    "timeline",
    "lộ trình",
    "lo trinh",
    "checklist",
    "tóm tắt",
    "tom tat",
    "so sánh phương thức",
    "so sanh phuong thuc",
    "hành động",
    "hanh dong",
    "tài liệu",
    "tai lieu",
]


def should_use_rag_first(question: str) -> bool:
    normalized_question = question.lower().strip()
    if not contains_any(normalized_question, ADMISSION_KEYWORDS):
        return False

    if contains_any(normalized_question, STRUCTURED_ACTION_KEYWORDS):
        return False

    return contains_any(normalized_question, RAG_FIRST_ADMISSION_KEYWORDS)


def build_references_from_structured_data(data: dict | None) -> list[dict]:
    if not data:
        return []

    data_type = data.get("type")
    title = data.get("title", "Dữ liệu nội bộ")

    if data_type in {"pdf_document", "document_file"}:
        return [
            {
                "title": data.get("name") or title,
                "domain": data.get("document_type") or data_type,
                "source_file": data.get("file_name") or data.get("source_file") or "data/json",
                "file_url": data.get("file_url", ""),
                "download_url": data.get("download_url") or data.get("file_url", ""),
                "file_type": data.get("file_type", ""),
            }
        ]

    if data_type == "document_collection":
        return [
            {
                "title": document.get("name") or document.get("title", ""),
                "domain": document.get("document_type", "Tài liệu"),
                "source_file": document.get("file_name", ""),
                "file_url": document.get("file_url", ""),
                "download_url": document.get("download_url") or document.get("file_url", ""),
                "file_type": document.get("file_type", ""),
            }
            for document in data.get("documents", [])
        ]

    return [
        {
            "title": title,
            "domain": data_type or "structured",
            "source_file": data.get("source_file") or "data/json",
            "file_url": "",
            "download_url": "",
            "file_type": "",
            "note": data.get("source_note", ""),
        }
    ]


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

    if should_use_rag_first(clean_question):
        context, references = build_rag_context(clean_question)
        if not context:
            context = build_context(clean_question)
        structured_hint = build_direct_context(clean_question)
        answer = ask_ollama(clean_question, context)
        return {
            "reply": answer,
            "data": None,
            "suggestions": get_contextual_suggestions(clean_question, structured_hint),
            "references": references if context else [],
            "source": "ollama",
        }

    structured_data = build_direct_context(clean_question)
    if structured_data and structured_data.get("type") == "text" and structured_data.get("source_note"):
        return {
            "reply": structured_data.get("title", ""),
            "data": structured_data,
            "suggestions": get_contextual_suggestions(clean_question, structured_data),
            "references": build_references_from_structured_data(structured_data),
            "source": "structured",
        }

    if structured_data and structured_data.get("type") in STRUCTURED_RESPONSE_TYPES:
        return {
            "reply": structured_data.get("title", ""),
            "data": structured_data,
            "suggestions": get_contextual_suggestions(clean_question, structured_data),
            "references": build_references_from_structured_data(structured_data),
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
