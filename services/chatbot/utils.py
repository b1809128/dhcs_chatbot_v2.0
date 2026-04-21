import json
from typing import Iterable, List

from .config import DATA_DIR
from .types import JsonDict, StructuredContext


def load_data(filename: str) -> JsonDict:
    candidate_paths = [
        DATA_DIR / "json" / filename,
        DATA_DIR / filename,
    ]

    path = next((item for item in candidate_paths if item.exists()), None)
    if path is None:
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


def build_pdf_document_context(
    title: str,
    *,
    document_type: str,
    name: str,
    so_hieu: str = "",
    ngay_ban_hanh: str = "",
    ngay_hieu_luc: str = "",
    trang_thai: str = "",
    tom_tat: str = "",
    noi_dung: str = "",
    co_quan_ban_hanh: str = "",
    file_url: str = "",
    file_name: str = "",
) -> StructuredContext:
    return {
        "type": "pdf_document",
        "title": title,
        "document_type": document_type,
        "name": name,
        "so_hieu": so_hieu,
        "ngay_ban_hanh": ngay_ban_hanh,
        "ngay_hieu_luc": ngay_hieu_luc,
        "trang_thai": trang_thai,
        "tom_tat": tom_tat,
        "noi_dung": noi_dung,
        "co_quan_ban_hanh": co_quan_ban_hanh,
        "file_url": file_url,
        "file_name": file_name,
    }


def build_document_file_context(
    title: str,
    *,
    document_type: str,
    name: str,
    description: str = "",
    file_url: str = "",
    file_name: str = "",
    file_type: str = "",
    download_url: str = "",
) -> StructuredContext:
    return {
        "type": "document_file",
        "title": title,
        "document_type": document_type,
        "name": name,
        "noi_dung": description,
        "tom_tat": description,
        "file_url": file_url,
        "file_name": file_name,
        "file_type": file_type,
        "download_url": download_url or file_url,
    }


def build_document_collection_context(
    title: str,
    *,
    description: str,
    documents: List[JsonDict],
) -> StructuredContext:
    return {
        "type": "document_collection",
        "title": title,
        "description": description,
        "documents": documents,
    }


def format_context_data(data: StructuredContext) -> str:
    context_type = data.get("type")
    title = data.get("title", "")
    source_note = data.get("source_note", "")

    if context_type == "text":
        message = data.get("message", "")
        body = f"=== {title} ===\n{message}" if title else message
        return f"{body}\n{source_note}" if source_note else body

    if context_type == "list":
        lines = [f"=== {title} ==="] if title else []
        for item in data.get("items", []):
            lines.append(f"- {item}")
        if source_note:
            lines.append(source_note)
        return "\n".join(lines)

    if context_type == "table":
        lines = [f"=== {title} ==="] if title else []
        columns = data.get("columns", [])
        if columns:
            lines.append(" | ".join(columns))
        for row in data.get("rows", []):
            lines.append(" | ".join(str(value) for value in row.values()))
        if source_note:
            lines.append(source_note)
        return "\n".join(lines)

    if context_type == "pdf_document":
        lines = [f"=== {title} ==="] if title else []
        lines.append(f"Tên văn bản: {data.get('name', '')}")
        if data.get("so_hieu"):
            lines.append(f"Số hiệu: {data.get('so_hieu', '')}")
        if data.get("ngay_hieu_luc"):
            lines.append(f"Ngày hiệu lực: {data.get('ngay_hieu_luc', '')}")
        if data.get("tom_tat"):
            lines.append(f"Tóm tắt: {data.get('tom_tat', '')}")
        if source_note:
            lines.append(source_note)
        return "\n".join(lines)

    if context_type == "document_file":
        lines = [f"=== {title} ==="] if title else []
        lines.append(f"Tên tài liệu: {data.get('name', '')}")
        if data.get("tom_tat"):
            lines.append(f"Tóm tắt: {data.get('tom_tat', '')}")
        if data.get("file_name"):
            lines.append(f"File: {data.get('file_name', '')}")
        if source_note:
            lines.append(source_note)
        return "\n".join(lines)

    if context_type == "document_collection":
        lines = [f"=== {title} ==="] if title else []
        if data.get("description"):
            lines.append(data.get("description", ""))
        for item in data.get("documents", []):
            lines.append(f"- {item.get('name', '')}: {item.get('file_name', '')}")
        if source_note:
            lines.append(source_note)
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
