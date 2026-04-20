from typing import Optional

from .keywords import DOCUMENT_KEYWORDS
from .types import JsonDict, StructuredContext
from .utils import (
    build_pdf_document_context,
    build_table_context,
    build_text_context,
    contains_any,
    load_data,
)

DOCUMENT_TABLE_FIELDS = ("ten", "so_hieu", "ngay_ban_hanh", "noi_dung", "trang_thai")
DOCUMENT_TABLE_COLUMNS = ["Tên", "Số hiệu", "Ngày ban hành", "Nội dung", "Trạng thái"]
PDF_METADATA_FIELDS = ("ngay_hieu_luc", "tom_tat", "co_quan_ban_hanh")


def _normalize_document_token(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum())


def _build_document_file_url(file_path: str) -> str:
    return f"/documents/{file_path}" if file_path else ""


def _build_document_file_name(file_path: str) -> str:
    return file_path.rsplit("/", 1)[-1] if file_path else ""


def _build_pdf_document(item: JsonDict, document_type: str) -> StructuredContext:
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
        file_url=_build_document_file_url(file_path),
        file_name=_build_document_file_name(file_path),
    )


def _build_basic_document_rows(items: list[JsonDict]) -> list[JsonDict]:
    return [
        {field: item.get(field, "") for field in DOCUMENT_TABLE_FIELDS}
        for item in items
    ]


def _build_pdf_ready_document_rows(
    items: list[JsonDict],
    *,
    document_type: str,
) -> list[JsonDict]:
    rows = []

    for item in items:
        row = {field: item.get(field, "") for field in DOCUMENT_TABLE_FIELDS}
        file_path = item.get("file_pdf", "")

        row.update(
            {
                "document_type": document_type,
                "file_url": _build_document_file_url(file_path),
                "file_name": _build_document_file_name(file_path),
            }
        )

        for field in PDF_METADATA_FIELDS:
            row[field] = item.get(field, "")

        rows.append(row)

    return rows


def _find_pdf_document(
    query: str,
    items: list[JsonDict],
    document_type: str,
) -> Optional[StructuredContext]:
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
            return _build_pdf_document(item, document_type)

    return None


def _build_document_table(
    title: str,
    rows: list[JsonDict],
    *,
    empty_message: str,
    include_quick_access: bool = False,
) -> StructuredContext:
    columns = list(DOCUMENT_TABLE_COLUMNS)
    if include_quick_access:
        columns.append("Truy cập nhanh")

    return build_table_context(
        title,
        columns,
        rows,
        empty_message=empty_message,
    )


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
        thong_tu_items = data.get("thong_tu", [])
        if matched_pdf := _find_pdf_document(query, thong_tu_items, "Thông tư"):
            return matched_pdf

        rows = _build_pdf_ready_document_rows(thong_tu_items, document_type="Thông tư")
        return _build_document_table(
            "THÔNG TƯ",
            rows,
            include_quick_access=True,
            empty_message="Hiện chưa có dữ liệu thông tư.",
        )

    if "nghị định" in query:
        nghi_dinh_items = data.get("nghi_dinh", [])
        if matched_pdf := _find_pdf_document(query, nghi_dinh_items, "Nghị định"):
            return matched_pdf

        rows = _build_basic_document_rows(nghi_dinh_items)
        return _build_document_table(
            "NGHỊ ĐỊNH",
            rows,
            empty_message="Hiện chưa có dữ liệu nghị định.",
        )

    if "luật" in query or "luat" in query:
        law_items = data.get("luat", [])

        if matched_pdf := _find_pdf_document(query, law_items, "Luật"):
            return matched_pdf

        if len(law_items) == 1:
            return _build_pdf_document(law_items[0], "Luật")

        rows = _build_basic_document_rows(law_items)
        return _build_document_table(
            "LUẬT",
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
