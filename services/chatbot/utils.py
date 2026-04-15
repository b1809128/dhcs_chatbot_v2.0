import json
from typing import Iterable, List

from .config import DATA_DIR
from .types import JsonDict, StructuredContext


def load_data(filename: str) -> JsonDict:
    path = DATA_DIR / filename
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def build_text_context(title: str, message: str) -> StructuredContext:
    return {
        "type": "text",
        "title": title,
        "message": message,
    }


def build_list_context(
    title: str,
    items: Iterable[str],
    *,
    empty_message: str | None = None,
) -> StructuredContext:
    rows = [item for item in items if item]
    if not rows and empty_message:
        return build_text_context(title, empty_message)

    return {
        "type": "list",
        "title": title,
        "items": rows,
    }


def build_table_context(
    title: str,
    columns: List[str],
    rows: List[JsonDict],
    *,
    empty_message: str | None = None,
) -> StructuredContext:
    if not rows and empty_message:
        return build_text_context(title, empty_message)

    return {
        "type": "table",
        "title": title,
        "columns": columns,
        "rows": rows,
    }


def format_context_data(data: StructuredContext) -> str:
    context_type = data.get("type")
    title = data.get("title", "")

    if context_type == "text":
        message = data.get("message", "")
        return f"=== {title} ===\n{message}" if title else message

    if context_type == "list":
        lines = [f"=== {title} ==="] if title else []
        for item in data.get("items", []):
            lines.append(f"- {item}")
        return "\n".join(lines)

    if context_type == "table":
        lines = [f"=== {title} ==="] if title else []
        columns = data.get("columns", [])
        if columns:
            lines.append(" | ".join(columns))
        for row in data.get("rows", []):
            lines.append(" | ".join(str(value) for value in row.values()))
        return "\n".join(lines)

    return ""


def find_books_by_name(books: Iterable[JsonDict], query: str) -> List[JsonDict]:
    return [
        book
        for book in books
        if any(
            keyword
            for keyword in [
                book.get("ten_sach", "").lower(),
                book.get("ma_tai_lieu", "").lower(),
                book.get("isbn", "").lower(),
                book.get("tac_gia", "").lower(),
                book.get("linh_vuc", "").lower(),
                *(item.lower() for item in book.get("tu_khoa", [])),
            ]
            if keyword and keyword in query
        )
    ]
