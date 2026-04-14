import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2:1.5b"

JsonDict = Dict[str, Any]
StructuredContext = Dict[str, Any]
ContextBuilder = Callable[[str], Optional[StructuredContext]]

SCHEDULE_KEYWORDS = [
    "lịch học",
    "lịch thi",
    "thời khóa biểu",
    "phòng",
    "phòng học",
    "phòng thi",
    "lớp",
    "giảng viên",
    "học hôm nay",
    "thi khi nào",
    "ngày thi",
    "dths3",
    "thahs",
    "qlhc",
    "kths",
    "luật hình sự",
    "tố tụng hình sự",
    "quản lý hành chính",
    "kỹ thuật hình sự",
]

DOCUMENT_KEYWORDS = [
    "công văn",
    "thông tư",
    "nghị định",
    "đảng viên",
    "đoàn thanh niên",
    "biểu mẫu",
    "đơn",
    "đơn xin phép",
    "đơn nghỉ",
    "tranh thủ",
    "đơn nghỉ tranh thủ",
    "công tác đoàn",
    "tổ chức",
]

STUDY_MATERIAL_KEYWORDS = [
    "học",
    "bài",
    "môn",
    "kiến thức",
    "tài liệu",
    "giáo trình",
    "file",
    "pdf",
    "giải thích",
    "không hiểu",
    "giảng lại",
    "hiểu bài",
    "ôn",
    "ôn tập",
    "luyện",
    "câu hỏi",
    "trắc nghiệm",
    "tóm tắt",
    "tóm lược",
    "ghi nhớ",
    "ý chính",
    "phương pháp học",
    "tự học",
    "ví dụ",
    "minh họa",
    "luật",
    "hình sự",
    "hành chính",
    "tố tụng",
    "nghiệp vụ",
    "pháp luật đại cương",
]

LIBRARY_KEYWORDS = [
    "sách",
    "thư viện",
    "mượn",
    "tìm sách",
    "có sách",
    "còn sách",
    "hết sách",
    "ở đâu",
    "kệ",
    "vị trí",
    "mượn bao lâu",
    "thời gian mượn",
    "luật",
    "hình sự",
    "tố tụng",
    "hành chính",
    "nghiệp vụ",
    "giáo trình luật hình sự",
    "luật tố tụng hình sự",
    "nghiệp vụ công an cơ bản",
    "pháp luật đại cương",
    "giáo trình quản lý hành chính",
    "kỹ thuật hình sự cơ bản",
    "giờ mở cửa",
    "mở cửa",
    "đóng cửa",
    "thủ thư",
    "liên hệ thư viện",
    "mượn tối đa",
    "gia hạn",
    "trả trễ",
    "phạt",
    "isbn",
    "mã tài liệu",
    "tác giả",
    "chỉ đọc tại chỗ",
]

ADMISSION_KEYWORDS = [
    "tuyển sinh",
    "chính quy",
    "văn bằng 2",
    "xét tuyển thẳng",
    "thi tuyển",
    "vb2ca",
    "liên thông",
    "thạc sĩ",
    "nghiên cứu sinh",
    "vừa học vừa làm",
    "sức khỏe",
    "tiếng anh",
    "chứng chỉ",
    "lý lịch",
    "ngành",
    "thông báo tuyển",
    "chỉ tiêu",
    "phương thức",
    "xét tuyển",
    "bài thi",
    "ca1",
    "ca2",
    "ca3",
    "ca4",
    "tổ hợp",
    "mã trường",
    "mã ngành",
    "phía nam",
    "đối tượng dự tuyển",
    "điều kiện dự tuyển",
    "hồ sơ nhập học",
    "hồ sơ",
    "nhập học",
    "email",
    "mail",
    "liên hệ",
    "website",
    "ngưỡng đầu vào",
]

ADMISSION_PRIORITY_KEYWORDS = [
    "tuyển sinh",
    "văn bằng 2",
    "vb2ca",
    "chỉ tiêu",
    "xét tuyển",
    "xét tuyển thẳng",
    "thi tuyển",
    "phương thức",
    "điều kiện",
    "bài thi",
    "ca1",
    "ca2",
    "ca3",
    "ca4",
    "mã trường",
    "mã ngành",
    "phía nam",
    "ngưỡng đầu vào",
    "hồ sơ",
    "nhập học",
    "ielts",
    "chứng chỉ",
    "liên hệ",
    "website",
]


def load_data(filename: str) -> JsonDict:
    path = DATA_DIR / filename
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def is_admission_query(text: str) -> bool:
    return contains_any(text, ADMISSION_PRIORITY_KEYWORDS)


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
    empty_message: Optional[str] = None,
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
    empty_message: Optional[str] = None,
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


def build_schedule_context(query: str) -> Optional[StructuredContext]:
    if not contains_any(query, SCHEDULE_KEYWORDS):
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
            if not item.get("mon", "").lower() or item.get("mon", "").lower() in query
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
            ["Tên", "Số hiệu", "Ngày ban hành",
                "Nội dung", "Đối tượng", "Trạng thái"],
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

    def build_rows(filter_fn: Callable[[str], bool]) -> List[JsonDict]:
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
        rows = build_rows(
            lambda ten: "ôn" in ten or "câu hỏi" in ten or "học" in ten)
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
            {
                "muc": "Thứ hai đến thứ sáu",
                "chi_tiet": opening_hours.get("thu_hai_den_thu_sau", ""),
            },
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
            {
                "muc": "Đối tượng áp dụng",
                "chi_tiet": ", ".join(borrowing_rules.get("doi_tuong_ap_dung", [])),
            },
            {
                "muc": "Số sách mượn tối đa",
                "chi_tiet": str(borrowing_rules.get("so_sach_muon_toi_da", "")),
            },
            {
                "muc": "Thời hạn mượn mặc định",
                "chi_tiet": borrowing_rules.get("thoi_han_muon_mac_dinh", ""),
            },
            {
                "muc": "Được gia hạn",
                "chi_tiet": "Có" if borrowing_rules.get("duoc_gia_han") else "Không",
            },
            {
                "muc": "Số lần gia hạn tối đa",
                "chi_tiet": str(borrowing_rules.get("so_lan_gia_han_toi_da", "")),
            },
            {
                "muc": "Thời gian gia hạn",
                "chi_tiet": borrowing_rules.get("thoi_gian_gia_han", ""),
            },
            {
                "muc": "Mức phạt trả trễ",
                "chi_tiet": borrowing_rules.get("muc_phat_tra_tre", ""),
            },
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


def build_admission_context(query: str) -> Optional[StructuredContext]:
    if not contains_any(query, ADMISSION_KEYWORDS):
        return None

    data = load_data("tuyen_sinh.json")
    if not data:
        return build_text_context("TUYỂN SINH", "Không thể tải dữ liệu tuyển sinh.")

    ts = data.get("tuyen_sinh_dai_hoc_chinh_quy", {})

    if "chỉ tiêu" in query:
        chi_tieu = ts.get("chi_tieu", {})
        tong = chi_tieu.get("tong_chi_tieu", "chưa có")
        pt1 = chi_tieu.get("phuong_thuc_1", {})
        pt2 = chi_tieu.get(
            "phuong_thuc_2", chi_tieu.get("phuong_thuc_2_3", {}))
        return build_table_context(
            "TUYỂN SINH",
            ["Nội dung", "Nam", "Nữ"],
            [
                {"noi_dung": f"Tổng chỉ tiêu năm 2026: {tong}", "nam": "", "nu": ""},
                {"noi_dung": "Phương thức 1", "nam": pt1.get(
                    "nam", 0), "nu": pt1.get("nu", 0)},
                {
                    "noi_dung": "Phương thức 2",
                    "nam": pt2.get("nam", 0),
                    "nu": pt2.get("nu", 0),
                },
            ],
        )

    if "phương thức" in query or "xét tuyển" in query:
        return build_table_context(
            "TUYỂN SINH",
            ["Mã", "Tên phương thức", "Mô tả"],
            [
                {
                    "ma": phuong_thuc.get("ma", ""),
                    "ten": phuong_thuc.get("ten", ""),
                    "mo_ta": phuong_thuc.get("mo_ta", ""),
                }
                for phuong_thuc in ts.get("phuong_thuc_tuyen_sinh", [])
            ],
            empty_message="Chưa có dữ liệu phương thức tuyển sinh.",
        )

    if "điều kiện" in query or "lý lịch" in query or "sức khỏe" in query:
        return build_list_context(
            "TUYỂN SINH",
            ts.get("dieu_kien_chung", []),
            empty_message="Chưa có dữ liệu điều kiện dự tuyển.",
        )

    if "chứng chỉ" in query or "tiếng anh" in query or "ielts" in query:
        pt2 = ts.get("dieu_kien_theo_phuong_thuc", {}).get("phuong_thuc_2", {})
        rows = [
            {"loai": "Yêu cầu chung", "chi_tiet": yeu_cau}
            for yeu_cau in pt2.get("yeu_cau_chung", [])
        ]
        rows.extend(
            {
                "loai": ten_chung_chi,
                "chi_tiet": muc,
            }
            for ten_chung_chi, muc in pt2.get("chung_chi_ngoai_ngu", {}).items()
        )
        return build_table_context(
            "TUYỂN SINH",
            ["Loại", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu chứng chỉ ngoại ngữ.",
        )

    if (
        "bài thi" in query
        or "vb2ca" in query
        or "ngưỡng đầu vào" in query
        or contains_any(query, ["ca1", "ca2", "ca3", "ca4"])
    ):
        bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
        rows = [
            {
                "ma": item.get("ma", ""),
                "tu_luan_bat_buoc": item.get("tu_luan_bat_buoc", ""),
                "trac_nghiem_bat_buoc": ", ".join(item.get("trac_nghiem_bat_buoc", [])),
                "trac_nghiem_tu_chon": item.get("trac_nghiem_tu_chon", ""),
            }
            for item in bai_thi.get("cac_ma_bai_thi", [])
        ]
        return build_table_context(
            "BÀI THI ĐÁNH GIÁ",
            ["Mã", "Tự luận bắt buộc", "Trắc nghiệm bắt buộc", "Môn tự chọn"],
            rows,
            empty_message="Chưa có dữ liệu bài thi đánh giá.",
        )

    if "hồ sơ" in query or "nhập học" in query:
        return build_list_context(
            "HỒ SƠ TUYỂN SINH",
            ts.get("ho_so_nhap_hoc", []),
            empty_message="Chưa có dữ liệu hồ sơ tuyển sinh.",
        )

    if "ngành" in query or "tổ hợp" in query or "mã ngành" in query:
        return build_table_context(
            "NGÀNH TUYỂN SINH",
            ["Tên ngành", "Mã ngành", "Mã trường",
                "Địa bàn", "Tổ hợp xét tuyển", "Mã bài thi"],
            [
                {
                    "ten_nganh": nganh.get("ten_nganh", ""),
                    "ma_nganh": nganh.get("ma_nganh", ""),
                    "ma_truong": nganh.get("ma_truong", ""),
                    "dia_ban": nganh.get("dia_ban", ""),
                    "to_hop_xet_tuyen": ", ".join(nganh.get("to_hop_xet_tuyen_pt3", [])),
                    "ma_bai_thi_danh_gia": ", ".join(nganh.get("ma_bai_thi_danh_gia", [])),
                }
                for nganh in ts.get("nganh_tuyen_sinh", [])
            ],
            empty_message="Chưa có dữ liệu ngành tuyển sinh.",
        )

    if "mã trường" in query or "css" in query or "trường" in query:
        thong_tin = data.get("thong_tin_chung", {})
        dia_chi = thong_tin.get("dia_chi", {})
        rows = [
            {"muc": "Tên trường", "chi_tiet": thong_tin.get(
                "ten_truong_vi", "")},
            {"muc": "Tên tiếng Anh", "chi_tiet": thong_tin.get(
                "ten_truong_en", "")},
            {"muc": "Mã trường", "chi_tiet": thong_tin.get("ma_truong", "")},
            {"muc": "Website", "chi_tiet": thong_tin.get("website", "")},
            {"muc": "Email tuyển sinh", "chi_tiet": thong_tin.get(
                "email_tuyen_sinh", "")},
            {"muc": "Trụ sở chính", "chi_tiet": dia_chi.get(
                "tru_so_chinh", "")},
            {"muc": "Cơ sở 2", "chi_tiet": dia_chi.get("co_so_2", "")},
            {"muc": "Cơ sở 3", "chi_tiet": dia_chi.get("co_so_3", "")},
        ]
        rows.extend(
            {
                "muc": f"Liên hệ tuyển sinh - {item.get('ho_ten', '')}",
                "chi_tiet": item.get("so_dien_thoai", ""),
            }
            for item in thong_tin.get("lien_he_tuyen_sinh", [])
        )
        return build_table_context("THÔNG TIN TRƯỜNG", ["Mục", "Chi tiết"], rows)

    if "email" in query or "mail" in query or "liên hệ" in query:
        thong_tin = data.get("thong_tin_chung", {})
        rows = [
            {"muc": "Website", "chi_tiet": thong_tin.get("website", "")},
            {"muc": "Email tuyển sinh", "chi_tiet": thong_tin.get(
                "email_tuyen_sinh", "")},
        ]
        rows.extend(
            {
                "muc": item.get("ho_ten", ""),
                "chi_tiet": item.get("so_dien_thoai", ""),
            }
            for item in thong_tin.get("lien_he_tuyen_sinh", [])
        )
        return build_table_context(
            "LIÊN HỆ TUYỂN SINH",
            ["Mục", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu liên hệ tuyển sinh.",
        )

    return build_text_context(
        "TUYỂN SINH",
        (
            "Bạn hãy hỏi cụ thể hơn về tuyển sinh như chỉ tiêu, "
            "phương thức, điều kiện, chứng chỉ, bài thi VB2CA, hồ sơ hoặc ngành tuyển sinh."
        ),
    )


def build_context(query: str) -> Optional[str]:
    normalized_query = query.lower().strip()

    if schedule_result := build_schedule_context(normalized_query):
        return format_context_data(schedule_result)

    if admission_result := build_admission_context(normalized_query):
        return format_context_data(admission_result)

    builders: List[ContextBuilder] = [
        build_document_context,
        build_study_material_context,
        build_library_context,
    ]

    context_parts = [
        format_context_data(result)
        for builder in builders
        if (result := builder(normalized_query))
    ]

    if not context_parts:
        return None

    return "\n\n".join(context_parts)


def build_direct_context(query: str) -> Optional[StructuredContext]:
    normalized_query = query.lower().strip()

    builders: List[ContextBuilder] = [
        build_schedule_context,
        build_admission_context,
        build_document_context,
        build_library_context,
        build_study_material_context,
    ]

    for builder in builders:
        result = builder(normalized_query)
        if result:
            return result

    return None


def get_contextual_suggestions(query: str, data: Optional[StructuredContext]) -> List[str]:
    normalized_query = query.lower().strip()
    title = (data or {}).get("title", "")

    if title == "LỊCH HỌC":
        if "dths3" in normalized_query:
            return [
                "Lịch thi",
                "Lịch học môn Luật Hình sự",
                "Lịch học môn Tố tụng hình sự",
                "Lịch học lớp THAHS",
            ]
        return [
            "Lịch học lớp DTHS3",
            "Lịch học lớp THAHS",
            "Lịch học môn Luật Hình sự",
            "Lịch thi",
        ]

    if title == "LỊCH THI":
        return [
            "Lịch thi Luật Hình sự",
            "Lịch thi Tố tụng hình sự",
            "Lịch thi Quản lý hành chính",
            "Lịch thi Kỹ thuật hình sự",
        ]

    if title in {"CÔNG VĂN", "THÔNG TƯ", "NGHỊ ĐỊNH", "BIỂU MẪU / ĐƠN", "TỔ CHỨC"}:
        if "đơn" in normalized_query:
            return [
                "Đơn nghỉ tranh thủ",
                "Công văn",
                "Thông tư",
                "Đoàn thanh niên",
            ]
        return [
            "Công văn",
            "Thông tư",
            "Nghị định",
            "Đơn xin phép",
        ]

    if title in {
        "THÔNG TIN THƯ VIỆN",
        "GIỜ MỞ CỬA THƯ VIỆN",
        "LIÊN HỆ THƯ VIỆN",
        "QUY ĐỊNH MƯỢN TRẢ",
        "SƠ ĐỒ KỆ THƯ VIỆN",
        "TÀI LIỆU ĐỌC TẠI CHỖ",
    }:
        if contains_any(normalized_query, ["giáo trình luật hình sự", "luật hình sự"]):
            return [
                "Luật Tố tụng hình sự",
                "Giờ mở cửa thư viện",
                "Mượn tối đa",
                "Liên hệ thư viện",
            ]
        return [
            "Giờ mở cửa thư viện",
            "Mượn tối đa",
            "Chỉ đọc tại chỗ",
            "Giáo trình Luật Hình sự",
        ]

    if title in {"TUYỂN SINH", "BÀI THI ĐÁNH GIÁ", "HỒ SƠ TUYỂN SINH", "NGÀNH TUYỂN SINH", "THÔNG TIN TRƯỜNG", "LIÊN HỆ TUYỂN SINH"}:
        if "chỉ tiêu" in normalized_query:
            return [
                "Phương thức tuyển sinh",
                "Điều kiện dự tuyển",
                "Hồ sơ nhập học",
                "Ngành tuyển sinh",
            ]
        if contains_any(normalized_query, ["vb2ca", "bài thi", "ca1", "ca2", "ca3", "ca4"]):
            return [
                "Ngưỡng đầu vào",
                "Chứng chỉ IELTS",
                "Hồ sơ nhập học",
                "Mã trường CSS",
            ]
        return [
            "Chỉ tiêu tuyển sinh",
            "Phương thức tuyển sinh",
            "Điều kiện dự tuyển",
            "Hồ sơ nhập học",
        ]

    if title == "TÀI LIỆU NGHIỆP VỤ":
        return [
            "Giải thích bài giảng",
            "Tóm tắt giáo trình",
            "Tạo câu hỏi ôn tập",
            "Gợi ý phương pháp học",
        ]

    return []


def ask_ollama(question: str, context: Optional[str]) -> str:
    system_prompt = (
        "Bạn là trợ lý hỗ trợ sinh viên trường Đại học Cảnh sát (ĐHCS). "
        "Chỉ trả lời dựa trên thông tin được cung cấp. "
        "Nếu không có thông tin, hãy nói 'Tôi chưa có thông tin về vấn đề này.' "
        "Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng."
    )

    prompt_parts = [system_prompt]
    if context:
        prompt_parts.append(f"Thông tin nội bộ:\n{context}")
    prompt_parts.append(f"Câu hỏi: {question}\nTrả lời:")
    prompt = "\n\n".join(prompt_parts)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 512},
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "❌ Không kết nối được Ollama. Hãy chắc chắn Ollama đang chạy (ollama serve)."
    except Exception as exc:
        return f"❌ Lỗi: {exc}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json() or {}
    question = payload.get("message", "").strip()

    if not question:
        return jsonify({"reply": "Vui lòng nhập câu hỏi.", "data": None})

    structured_data = build_direct_context(question)
    if structured_data:
        return jsonify(
            {
                "reply": structured_data.get("title", ""),
                "data": structured_data,
                "suggestions": get_contextual_suggestions(question, structured_data),
            }
        )

    context = build_context(question)
    answer = ask_ollama(question, context)
    return jsonify(
        {
            "reply": answer,
            "data": None,
            "suggestions": get_contextual_suggestions(question, None),
        }
    )


if __name__ == "__main__":
    print("🚀 Khởi động chatbot ĐHCS tại http://localhost:5000")
    app.run(debug=True, port=5000)
