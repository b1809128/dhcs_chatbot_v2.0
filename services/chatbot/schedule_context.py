from typing import Optional

from .keywords import SCHEDULE_KEYWORDS
from .types import StructuredContext
from .utils import build_table_context, build_text_context, contains_any, load_data


def build_schedule_context(query: str) -> Optional[StructuredContext]:
    if not contains_any(query, SCHEDULE_KEYWORDS):
        return None
    if contains_any(
        query,
        [
            "tuyển sinh",
            "tuyen sinh",
            "văn bằng 2",
            "văn bằng hai",
            "van bang 2",
            "van bang hai",
            "vb2",
            "vb2ca",
            "bài thi đánh giá",
            "20/09/2026",
        ],
    ):
        return None

    data = load_data("lich_hoc.json")
    if not data:
        return build_text_context("LỊCH", "Không có dữ liệu lịch học.")

    lich_hoc = data.get("lich_hoc", [])
    lich_thi = data.get("lich_thi", [])

    if "lịch thi" in query or "thi khi nào" in query:
        rows = [
            {
                "mon": item.get("mon", ""),
                "ngay_thi": item.get("ngay_thi", ""),
                "phong": item.get("phong", ""),
            }
            for item in lich_thi
            if item.get("mon", "").lower() and item.get("mon", "").lower() in query
        ]

        if not rows:
            rows = [
                {
                    "mon": item.get("mon", ""),
                    "ngay_thi": item.get("ngay_thi", ""),
                    "phong": item.get("phong", ""),
                }
                for item in lich_thi
            ]

        return build_table_context(
            "LỊCH THI",
            ["Môn", "Ngày thi", "Phòng thi"],
            rows,
            empty_message="Hiện chưa có dữ liệu lịch thi phù hợp.",
        )

    rows = [
        {
            "lop": item.get("lop", ""),
            "mon": item.get("mon", ""),
            "giang_vien": item.get("giang_vien", ""),
            "phong": item.get("phong", ""),
            "thoi_gian": item.get("thoi_gian", ""),
        }
        for item in lich_hoc
        if (item.get("lop", "").lower() and item.get("lop", "").lower() in query)
        or (item.get("mon", "").lower() and item.get("mon", "").lower() in query)
    ]

    if not rows:
        rows = [
            {
                "lop": item.get("lop", ""),
                "mon": item.get("mon", ""),
                "giang_vien": item.get("giang_vien", ""),
                "phong": item.get("phong", ""),
                "thoi_gian": item.get("thoi_gian", ""),
            }
            for item in lich_hoc
        ]

    return build_table_context(
        "LỊCH HỌC",
        ["Lớp", "Môn", "Giảng viên", "Phòng", "Thời gian"],
        rows,
    )
