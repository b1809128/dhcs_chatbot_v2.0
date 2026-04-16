from typing import Optional

from .keywords import DOCUMENT_KEYWORDS
from .types import StructuredContext
from .utils import (
    build_pdf_document_context,
    build_table_context,
    build_text_context,
    contains_any,
    load_data,
)


def _normalize_document_token(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum())


def _find_pdf_document(query: str, items: list[dict], document_type: str) -> Optional[StructuredContext]:
    normalized_query = _normalize_document_token(query)

    for item in items:
        candidates = [
            item.get("ten", ""),
            item.get("so_hieu", ""),
            item.get("file_pdf", ""),
            *(item.get("tu_khoa", []) or []),
        ]

        if any(
            token
            and (
                token.lower() in query
                or _normalize_document_token(token) in normalized_query
            )
            for token in candidates
        ):
            file_path = item.get("file_pdf", "")
            return build_pdf_document_context(
                title=document_type.upper(),
                document_type=document_type,
                name=item.get("ten", ""),
                so_hieu=item.get("so_hieu", ""),
                ngay_ban_hanh=item.get("ngay_ban_hanh", ""),
                ngay_hieu_luc=item.get("ngay_hieu_luc", ""),
                trang_thai=item.get("trang_thai", ""),
                tom_tat=item.get("tom_tat", ""),
                noi_dung=item.get("noi_dung", ""),
                co_quan_ban_hanh=item.get("co_quan_ban_hanh", ""),
                file_url=f"/documents/{file_path}" if file_path else "",
                file_name=file_path.rsplit("/", 1)[-1] if file_path else "",
            )

    return None


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
        if matched_pdf := _find_pdf_document(query, data.get("thong_tu", []), "Thông tư"):
            return matched_pdf

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
        if matched_pdf := _find_pdf_document(query, data.get("nghi_dinh", []), "Nghị định"):
            return matched_pdf

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

    if any(keyword in query for keyword in ["luật an ninh mạng", "luat an ninh mang", "luat_an_ninh_mang"]):
        if matched_pdf := _find_pdf_document(query, data.get("luat", []), "Luật"):
            return matched_pdf

        rows = [
            {
                "ten": item.get("ten", ""),
                "so_hieu": item.get("so_hieu", ""),
                "ngay_ban_hanh": item.get("ngay_ban_hanh", ""),
                "noi_dung": item.get("noi_dung", ""),
                "trang_thai": item.get("trang_thai", ""),
            }
            for item in data.get("luat", [])
        ]
        return build_table_context(
            "LUẬT",
            ["Tên", "Số hiệu", "Ngày ban hành", "Nội dung", "Trạng thái"],
            rows,
            empty_message="Hiện chưa có dữ liệu luật.",
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
