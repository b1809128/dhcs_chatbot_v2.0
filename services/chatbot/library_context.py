from typing import Optional

from .keywords import ADMISSION_PRIORITY_KEYWORDS, LIBRARY_KEYWORDS
from .types import StructuredContext
from .utils import (
    build_table_context,
    contains_any,
    find_books_by_name,
    load_data,
)


def is_admission_query(text: str) -> bool:
    return contains_any(text, ADMISSION_PRIORITY_KEYWORDS)


def build_library_context(query: str) -> Optional[StructuredContext]:
    if is_admission_query(query):
        return None

    if not contains_any(query, LIBRARY_KEYWORDS):
        return None

    data = load_data("thu_vien.json")
    if not data:
        return None

    library_info = data.get("thong_tin_thu_vien", {})
    borrowing_rules = data.get("quy_dinh_muon_tra", {})
    shelves = data.get("danh_muc_ke", [])
    books = data.get("thu_vien", [])
    matched_books = find_books_by_name(books, query)

    if contains_any(query, ["giờ mở cửa", "mở cửa", "đóng cửa"]):
        opening_hours = library_info.get("gio_mo_cua", {})
        rows = [
            {"muc": "Thư viện", "chi_tiet": library_info.get("ten", "")},
            {"muc": "Địa điểm", "chi_tiet": library_info.get("dia_diem", "")},
            {"muc": "Thứ hai đến thứ sáu", "chi_tiet": opening_hours.get("thu_hai_den_thu_sau", "")},
            {"muc": "Thứ bảy", "chi_tiet": opening_hours.get("thu_bay", "")},
            {"muc": "Chủ nhật", "chi_tiet": opening_hours.get("chu_nhat", "")},
        ]
        return build_table_context(
            "GIỜ MỞ CỬA THƯ VIỆN",
            ["Mục", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu giờ mở cửa thư viện.",
        )

    if contains_any(query, ["liên hệ thư viện", "thủ thư", "số điện thoại", "email thư viện"]):
        contact = library_info.get("lien_he", {})
        rows = [
            {"muc": "Tên thư viện", "chi_tiet": library_info.get("ten", "")},
            {"muc": "Mã thư viện", "chi_tiet": library_info.get("ma_thu_vien", "")},
            {"muc": "Địa điểm", "chi_tiet": library_info.get("dia_diem", "")},
            {"muc": "Số điện thoại", "chi_tiet": contact.get("so_dien_thoai", "")},
            {"muc": "Email", "chi_tiet": contact.get("email", "")},
        ]
        return build_table_context(
            "LIÊN HỆ THƯ VIỆN",
            ["Mục", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu liên hệ thư viện.",
        )

    if contains_any(query, ["mượn tối đa", "gia hạn", "trả trễ", "phạt", "quy định mượn", "quy định thư viện"]):
        rows = [
            {"muc": "Đối tượng áp dụng", "chi_tiet": ", ".join(borrowing_rules.get("doi_tuong_ap_dung", []))},
            {"muc": "Số sách mượn tối đa", "chi_tiet": str(borrowing_rules.get("so_sach_muon_toi_da", ""))},
            {"muc": "Thời hạn mượn mặc định", "chi_tiet": borrowing_rules.get("thoi_han_muon_mac_dinh", "")},
            {"muc": "Được gia hạn", "chi_tiet": "Có" if borrowing_rules.get("duoc_gia_han") else "Không"},
            {"muc": "Số lần gia hạn tối đa", "chi_tiet": str(borrowing_rules.get("so_lan_gia_han_toi_da", ""))},
            {"muc": "Thời gian gia hạn", "chi_tiet": borrowing_rules.get("thoi_gian_gia_han", "")},
            {"muc": "Mức phạt trả trễ", "chi_tiet": borrowing_rules.get("muc_phat_tra_tre", "")},
        ]
        notes = borrowing_rules.get("ghi_chu", [])
        rows.extend(
            {"muc": f"Ghi chú {index}", "chi_tiet": note}
            for index, note in enumerate(notes, start=1)
        )
        return build_table_context(
            "QUY ĐỊNH MƯỢN TRẢ",
            ["Mục", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu quy định mượn trả.",
        )

    if contains_any(query, ["kệ", "vị trí", "danh mục kệ", "khu vực sách"]):
        return build_table_context(
            "SƠ ĐỒ KỆ THƯ VIỆN",
            ["Mã kệ", "Khu vực", "Vị trí"],
            [
                {
                    "ma_ke": shelf.get("ma_ke", ""),
                    "khu_vuc": shelf.get("khu_vuc", ""),
                    "vi_tri": shelf.get("vi_tri", ""),
                }
                for shelf in shelves
            ],
            empty_message="Chưa có dữ liệu sơ đồ kệ thư viện.",
        )

    if contains_any(query, ["chỉ đọc tại chỗ", "đọc tại chỗ", "tài liệu nội bộ"]):
        return build_table_context(
            "TÀI LIỆU ĐỌC TẠI CHỖ",
            ["Tên sách", "Mã tài liệu", "Vị trí", "Ghi chú"],
            [
                {
                    "ten_sach": book.get("ten_sach", ""),
                    "ma_tai_lieu": book.get("ma_tai_lieu", ""),
                    "vi_tri": book.get("ke_sach", ""),
                    "ghi_chu": book.get("ghi_chu", ""),
                }
                for book in books
                if "đọc tại chỗ" in book.get("hinh_thuc_khai_thac", "").lower()
            ],
            empty_message="Hiện chưa có tài liệu chỉ đọc tại chỗ.",
        )

    if matched_books:
        return build_table_context(
            "THÔNG TIN THƯ VIỆN",
            ["Tên sách", "Mã tài liệu", "Tác giả", "Vị trí kệ", "Tình trạng", "Thời gian mượn"],
            [
                {
                    "ten_sach": book.get("ten_sach", ""),
                    "ma_tai_lieu": book.get("ma_tai_lieu", ""),
                    "tac_gia": book.get("tac_gia", ""),
                    "ke_sach": book.get("ke_sach", ""),
                    "tinh_trang": book.get("tinh_trang", ""),
                    "thoi_gian_muon": book.get("thoi_gian_muon", ""),
                }
                for book in matched_books
            ],
        )

    if "còn sách" in query or "còn không" in query:
        return build_table_context(
            "THÔNG TIN THƯ VIỆN",
            ["Tên sách", "Số lượng còn", "Vị trí kệ", "Thời gian mượn"],
            [
                {
                    "ten_sach": book.get("ten_sach", ""),
                    "so_luong": book.get("so_luong", 0),
                    "ke_sach": book.get("ke_sach", ""),
                    "thoi_gian_muon": book.get("thoi_gian_muon", ""),
                }
                for book in books
                if book.get("so_luong", 0) > 0
            ],
            empty_message="Hiện không có sách còn trong thư viện.",
        )

    if "hết sách" in query or "hết chưa" in query:
        return build_table_context(
            "THÔNG TIN THƯ VIỆN",
            ["Tên sách", "Mã tài liệu", "Vị trí kệ"],
            [
                {
                    "ten_sach": book.get("ten_sach", ""),
                    "ma_tai_lieu": book.get("ma_tai_lieu", ""),
                    "ke_sach": book.get("ke_sach", ""),
                }
                for book in books
                if book.get("so_luong", 0) == 0
            ],
            empty_message="Hiện chưa có sách nào hết.",
        )

    return build_table_context(
        "THÔNG TIN THƯ VIỆN",
        ["Tên sách", "Lĩnh vực", "Tình trạng", "Vị trí kệ", "Thời gian mượn"],
        [
            {
                "ten_sach": book.get("ten_sach", ""),
                "linh_vuc": book.get("linh_vuc", ""),
                "tinh_trang": book.get("tinh_trang", ""),
                "ke_sach": book.get("ke_sach", ""),
                "thoi_gian_muon": book.get("thoi_gian_muon", ""),
            }
            for book in books
        ],
        empty_message="Chưa có dữ liệu thư viện.",
    )
