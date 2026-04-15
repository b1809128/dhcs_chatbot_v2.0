from typing import List, Optional

from .keywords import ADMISSION_PRIORITY_KEYWORDS, STUDY_MATERIAL_KEYWORDS
from .types import JsonDict, StructuredContext
from .utils import build_table_context, contains_any, load_data


def is_admission_query(text: str) -> bool:
    return contains_any(text, ADMISSION_PRIORITY_KEYWORDS)


def build_study_material_context(query: str) -> Optional[StructuredContext]:
    if is_admission_query(query):
        return None

    if not contains_any(query, STUDY_MATERIAL_KEYWORDS):
        return None

    data = load_data("tai_lieu.json")
    if not data:
        return None

    chuc_nang = data.get("chuc_nang", [])
    linh_vuc = ", ".join(data.get("linh_vuc", []))

    def build_rows(filter_fn) -> List[JsonDict]:
        return [
            {
                "chuc_nang": item.get("ten", ""),
                "noi_dung": "; ".join(item.get("noi_dung", [])),
                "linh_vuc": linh_vuc,
            }
            for item in chuc_nang
            if filter_fn(item.get("ten", "").lower())
        ]

    if contains_any(query, ["ôn", "ôn tập", "luyện", "câu hỏi", "trắc nghiệm"]):
        rows = build_rows(lambda ten: "ôn" in ten or "câu hỏi" in ten or "học" in ten)
    elif contains_any(query, ["giải thích", "không hiểu", "giảng lại", "hiểu bài"]):
        rows = build_rows(lambda ten: "giải thích" in ten or "giải đáp" in ten)
    elif contains_any(query, ["tóm tắt", "tóm lược", "ghi nhớ", "ý chính"]):
        rows = build_rows(lambda ten: "tóm tắt" in ten)
    else:
        rows = [
            {
                "chuc_nang": item.get("ten", ""),
                "noi_dung": "; ".join(item.get("noi_dung", [])),
                "linh_vuc": linh_vuc,
            }
            for item in chuc_nang
        ]

    return build_table_context(
        "TÀI LIỆU NGHIỆP VỤ",
        ["Chức năng", "Nội dung", "Lĩnh vực áp dụng"],
        rows,
        empty_message="Chưa có dữ liệu tài liệu nghiệp vụ phù hợp.",
    )
