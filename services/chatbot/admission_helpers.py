import re
import unicodedata

from .types import StructuredContext


SCHOOL_CODES = {"ANH", "ANS", "CSS", "PCH", "KTH"}

VB2CA_EXAM_FILES = {
    "CA1": "de_thi/CA1.pdf",
    "CA2": "de_thi/CA2.pdf",
    "CA3": "de_thi/CA3.pdf",
    "CA4": "de_thi/CA4.pdf",
}


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn").replace("đ", "d").replace("Đ", "D")


def normalize_admission_query(query: str) -> str:
    normalized = query.lower().strip()
    ascii_query = strip_accents(normalized)
    aliases = [
        "văn bằng hai",
        "van bang hai",
        "bằng đại học thứ 2",
        "bang dai hoc thu 2",
        "bằng đại học thứ hai",
        "bang dai hoc thu hai",
        "đại học thứ 2",
        "dai hoc thu 2",
    ]
    expanded = f"{normalized} {ascii_query}"
    if any(alias in expanded for alias in aliases):
        expanded += " văn bằng 2 van bang 2 vb2"
    if "vb 2" in expanded or "vb-2" in expanded:
        expanded += " vb2 văn bằng 2 van bang 2"
    return expanded


def source_note(data: dict, section: str) -> str:
    source = data.get("nguon", {})
    source_name = source.get("ten_trang") or "Thông báo tuyển sinh VB2CA 2026"
    source_file = source.get("file_pdf") or "thong_tu/tuyen_sinh_2026.pdf"
    return f"Nguồn: data/json/tuyen_sinh.json; PDF: {source_file}; mục: {section}; {source_name}."


def with_source(context: StructuredContext, data: dict, section: str) -> StructuredContext:
    context["source_note"] = source_note(data, section)
    context["source_file"] = "tuyen_sinh.json"
    return context


def extract_school_code(query: str) -> str | None:
    upper_query = query.upper()
    for code in SCHOOL_CODES:
        if re.search(rf"\b{code}\b", upper_query):
            return code
    return None


def is_vb2_overview_query(query: str) -> bool:
    return "văn bằng 2" in query or "van bang 2" in query or ("vb2" in query and "vb2ca" not in query)
