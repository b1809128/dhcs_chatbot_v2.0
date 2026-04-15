from typing import Optional

from .keywords import DOCUMENT_KEYWORDS
from .types import StructuredContext
from .utils import build_table_context, build_text_context, contains_any, load_data


def build_document_context(query: str) -> Optional[StructuredContext]:
    if not contains_any(query, DOCUMENT_KEYWORDS):
        return None

    data = load_data("ho_so.json")
    if not data:
        return None

    if "công văn" in query:
        rows = [
            {
                "ten": item.get("ten", ""),
                "so_hieu": item.get("so_hieu", ""),
                "ngay_ban_hanh": item.get("ngay_ban_hanh", ""),
                "noi_dung": item.get("noi_dung", ""),
                "doi_tuong": item.get("doi_tuong", ""),
                "trang_thai": item.get("trang_thai", ""),
            }
            for item in data.get("cong_van", [])
        ]
        return build_table_context(
            "CÔNG VĂN",
            ["Tên", "Số hiệu", "Ngày ban hành", "Nội dung", "Đối tượng", "Trạng thái"],
            rows,
            empty_message="Hiện chưa có dữ liệu công văn.",
        )

    if "thông tư" in query:
        rows = [
            {
                "ten": item.get("ten", ""),
                "so_hieu": item.get("so_hieu", ""),
                "ngay_ban_hanh": item.get("ngay_ban_hanh", ""),
                "noi_dung": item.get("noi_dung", ""),
                "trang_thai": item.get("trang_thai", ""),
            }
            for item in data.get("thong_tu", [])
        ]
        return build_table_context(
            "THÔNG TƯ",
            ["Tên", "Số hiệu", "Ngày ban hành", "Nội dung", "Trạng thái"],
            rows,
            empty_message="Hiện chưa có dữ liệu thông tư.",
        )

    if "nghị định" in query:
        rows = [
            {
                "ten": item.get("ten", ""),
                "so_hieu": item.get("so_hieu", ""),
                "ngay_ban_hanh": item.get("ngay_ban_hanh", ""),
                "noi_dung": item.get("noi_dung", ""),
                "trang_thai": item.get("trang_thai", ""),
            }
            for item in data.get("nghi_dinh", [])
        ]
        return build_table_context(
            "NGHỊ ĐỊNH",
            ["Tên", "Số hiệu", "Ngày ban hành", "Nội dung", "Trạng thái"],
            rows,
            empty_message="Hiện chưa có dữ liệu nghị định.",
        )

    if "đơn" in query:
        items = data.get("bieu_mau", [])
        if not items:
            return build_text_context("BIỂU MẪU", "Hiện chưa có dữ liệu biểu mẫu.")

        matched_item = next(
            (
                item
                for item in items
                if item.get("ten", "").lower() and item.get("ten", "").lower() in query
            ),
            None,
        )
        if matched_item:
            return build_table_context(
                "BIỂU MẪU / ĐƠN",
                ["Tên biểu mẫu", "Mô tả", "Nội dung mẫu"],
                [
                    {
                        "ten": matched_item.get("ten", ""),
                        "mo_ta": matched_item.get("mo_ta", ""),
                        "noi_dung_mau": matched_item.get("noi_dung_mau", ""),
                    }
                ],
            )

        return build_table_context(
            "BIỂU MẪU / ĐƠN",
            ["Tên biểu mẫu", "Mô tả"],
            [
                {
                    "ten": item.get("ten", ""),
                    "mo_ta": item.get("mo_ta", ""),
                }
                for item in items
            ],
        )

    if "đoàn" in query or "đảng" in query:
        rows = [
            {
                "ten": item.get("ten", ""),
                "noi_dung": item.get("noi_dung", ""),
            }
            for item in data.get("to_chuc", [])
        ]
        return build_table_context(
            "TỔ CHỨC",
            ["Tên", "Nội dung"],
            rows,
            empty_message="Hiện chưa có dữ liệu tổ chức.",
        )

    return None
