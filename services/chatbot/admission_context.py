from typing import Optional

from .admission_helpers import (
    extract_school_code,
    is_vb2_overview_query,
    normalize_admission_query,
    with_source,
)
from .admission_precheck import build_precheck_context, has_profile_signals
from .admission_views import (
    build_admission_action_documents,
    build_admission_quota_rows,
    build_admission_summary_rows,
    build_admission_timeline_rows,
    build_method_comparison_rows,
    build_vb2ca_exam_documents,
    build_vb2ca_overview_rows,
)
from .keywords import ADMISSION_KEYWORDS
from .types import StructuredContext
from .utils import (
    build_document_collection_context,
    build_list_context,
    build_table_context,
    build_text_context,
    contains_any,
    load_data,
)


def _build_conflict_context(data: dict) -> StructuredContext:
    return with_source(
        build_text_context(
            "LƯU Ý MÂU THUẪN",
            (
                "Dữ liệu tuyển sinh VB2CA hiện nêu rõ không tuyển sinh đối tượng trình độ liên thông đại học. "
                "Nếu thí sinh có bằng đại học chính quy khác, cần đối chiếu lại loại hình đào tạo ghi trên văn bằng/hồ sơ."
            ),
        ),
        data,
        "điều kiện chung",
    )


def _build_professional_context(query: str, data: dict, ts: dict) -> Optional[StructuredContext]:
    if contains_any(query, ["tóm tắt", "tom tat", "card", "tổng quan nhanh", "tong quan nhanh"]):
        return with_source(
            build_table_context(
                "TÓM TẮT TUYỂN SINH VB2CA 2026",
                ["Mục", "Chi tiết"],
                build_admission_summary_rows(data, ts),
                empty_message="Chưa có dữ liệu tóm tắt tuyển sinh.",
            ),
            data,
            "thông tin tổng quan",
        )

    if contains_any(query, ["timeline", "lộ trình", "lo trinh", "mốc thời gian", "moc thoi gian", "thời gian tuyển sinh"]):
        return with_source(
            build_table_context(
                "TIMELINE TUYỂN SINH VB2CA 2026",
                ["Mốc", "Nội dung"],
                build_admission_timeline_rows(data, ts),
                empty_message="Chưa có dữ liệu timeline tuyển sinh.",
            ),
            data,
            "thời gian tuyển sinh, thủ tục đăng ký và bài thi đánh giá",
        )

    if contains_any(query, ["checklist", "danh sách hồ sơ", "danh sach ho so"]):
        return with_source(
            build_list_context(
                "CHECKLIST HỒ SƠ SƠ TUYỂN",
                ts.get("ho_so_nhap_hoc", []),
                empty_message="Chưa có dữ liệu checklist hồ sơ.",
            ),
            data,
            "hồ sơ nhập học/sơ tuyển",
        )

    if contains_any(query, ["so sánh phương thức", "so sanh phuong thuc", "so sánh pt1", "so sanh pt1", "pt1 và pt2", "pt1 va pt2"]):
        return with_source(
            build_table_context(
                "SO SÁNH PHƯƠNG THỨC TUYỂN SINH",
                ["Tiêu chí", "Phương thức 1", "Phương thức 2"],
                build_method_comparison_rows(ts, data),
                empty_message="Chưa có dữ liệu so sánh phương thức.",
            ),
            data,
            "phương thức tuyển sinh và xét tuyển",
        )

    if contains_any(
        query,
        ["nút hành động", "nut hanh dong", "hành động", "hanh dong", "tải thông báo", "tai thong bao", "xem đề", "xem de"],
    ):
        return with_source(
            build_document_collection_context(
                "TÀI LIỆU VÀ HÀNH ĐỘNG TUYỂN SINH",
                description="Các tài liệu tuyển sinh có thể xem nhanh hoặc tải về.",
                documents=build_admission_action_documents(data),
            ),
            data,
            "thông báo tuyển sinh và bài thi đánh giá",
        )

    return None


def _build_notice_context(query: str, data: dict) -> Optional[StructuredContext]:
    if not contains_any(query, ["thông báo 56", "56/tb-cat-px01", "56/TB-CAT-PX01", "thông báo tuyển"]):
        return None

    thong_bao = data.get("thong_bao_tuyen_sinh", {})
    return with_source(
        build_table_context(
            "THÔNG BÁO TUYỂN SINH",
            ["Mục", "Chi tiết"],
            [
                {"muc": "Số hiệu", "chi_tiet": thong_bao.get("so_hieu", "")},
                {"muc": "Tên thông báo", "chi_tiet": thong_bao.get("ten_thong_bao", "")},
                {"muc": "Cơ quan ban hành", "chi_tiet": thong_bao.get("co_quan_ban_hanh", "")},
                {"muc": "Ngày ban hành", "chi_tiet": thong_bao.get("ngay_ban_hanh", "")},
            ],
            empty_message="Chưa có dữ liệu thông báo tuyển sinh.",
        ),
        data,
        "thông báo tuyển sinh",
    )


def _build_procedure_context(query: str, ts: dict) -> Optional[StructuredContext]:
    if contains_any(query, ["phạm vi", "địa bàn", "phía nam", "toàn quốc"]):
        pham_vi = ts.get("pham_vi_tuyen_sinh", {})
        return build_table_context(
            "PHẠM VI TUYỂN SINH",
            ["Phạm vi", "Trường/ngành"],
            [
                {"pham_vi": "Toàn quốc", "truong_nganh": pham_vi.get("toan_quoc", "")},
                {"pham_vi": "Phía Nam", "truong_nganh": pham_vi.get("phia_nam", "")},
            ],
            empty_message="Chưa có dữ liệu phạm vi tuyển sinh.",
        )

    if contains_any(query, ["sơ tuyển", "lệ phí", "đăng ký dự tuyển", "thủ tục đăng ký", "hạn đăng ký"]):
        thu_tuc = ts.get("thu_tuc_dang_ky", {})
        return build_table_context(
            "THỦ TỤC SƠ TUYỂN",
            ["Mục", "Chi tiết"],
            [
                {"muc": "Nơi đăng ký", "chi_tiet": thu_tuc.get("noi_dang_ky", "")},
                {"muc": "Thời gian đăng ký", "chi_tiet": thu_tuc.get("thoi_gian_dang_ky", "")},
                {"muc": "Lệ phí sơ tuyển", "chi_tiet": thu_tuc.get("le_phi_so_tuyen", "")},
            ],
            empty_message="Chưa có dữ liệu thủ tục sơ tuyển.",
        )

    return None


def _build_policy_context(query: str, ts: dict) -> Optional[StructuredContext]:
    if contains_any(query, ["ưu tiên", "điểm thưởng", "ielts", "chứng chỉ", "tiếng anh"]):
        pt2 = ts.get("dieu_kien_theo_phuong_thuc", {}).get("phuong_thuc_2", {})
        rows = [{"loai": "Ưu tiên/điểm thưởng", "chi_tiet": item} for item in ts.get("uu_tien_trong_tuyen_sinh", [])]
        rows.extend(
            {"loai": ten_chung_chi, "chi_tiet": muc}
            for ten_chung_chi, muc in pt2.get("chung_chi_ngoai_ngu", {}).items()
        )
        return build_table_context(
            "ƯU TIÊN TUYỂN SINH",
            ["Loại", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu ưu tiên tuyển sinh.",
        )

    if contains_any(query, ["đào tạo", "thời gian đào tạo", "chính sách", "phân công", "phong hàm", "trung úy"]):
        dao_tao = ts.get("thoi_gian_dia_diem_dao_tao", {})
        rows = [
            {"muc": "Thời gian đào tạo", "chi_tiet": dao_tao.get("thoi_gian", "")},
            {"muc": "Địa điểm đào tạo", "chi_tiet": dao_tao.get("dia_diem", "")},
        ]
        rows.extend(
            {"muc": f"Chính sách {index}", "chi_tiet": item}
            for index, item in enumerate(ts.get("che_do_chinh_sach", []), start=1)
        )
        return build_table_context(
            "ĐÀO TẠO VÀ CHÍNH SÁCH",
            ["Mục", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu đào tạo và chính sách.",
        )

    return None


def _build_score_context(query: str, ts: dict) -> Optional[StructuredContext]:
    if not contains_any(query, ["cách tính điểm", "điểm xét tuyển", "công thức", "đxt", "điểm cộng"]):
        return None

    rows = [
        {"muc": f"Phương thức 1 - {index}", "chi_tiet": item}
        for index, item in enumerate(ts.get("xet_tuyen_va_tinh_diem", {}).get("phuong_thuc_1", []), start=1)
    ]
    rows.extend(
        {"muc": f"Phương thức 2 - {index}", "chi_tiet": item}
        for index, item in enumerate(ts.get("xet_tuyen_va_tinh_diem", {}).get("phuong_thuc_2", []), start=1)
    )
    return build_table_context(
        "XÉT TUYỂN VÀ CÁCH TÍNH ĐIỂM",
        ["Mục", "Chi tiết"],
        rows,
        empty_message="Chưa có dữ liệu xét tuyển và cách tính điểm.",
    )


def _build_quota_context(query: str, data: dict, ts: dict) -> Optional[StructuredContext]:
    if "chỉ tiêu" not in query:
        return None

    quota_items = ts.get("chi_tieu_theo_truong", [])
    school_code = extract_school_code(query)
    if school_code:
        quota_items = [item for item in quota_items if item.get("ma_truong") == school_code]

    if quota_items:
        return with_source(
            build_table_context(
                "CHỈ TIÊU TUYỂN SINH",
                ["Trường", "Mã trường", "Nhóm ngành", "Mã ngành", "Địa bàn", "Tổng", "PT1", "PT2"],
                build_admission_quota_rows(quota_items),
                empty_message="Chưa có dữ liệu chỉ tiêu tuyển sinh.",
            ),
            data,
            "chỉ tiêu theo trường",
        )

    chi_tieu = ts.get("chi_tieu", {})
    return with_source(
        build_table_context(
            "CHỈ TIÊU TUYỂN SINH",
            ["Nội dung", "Nam", "Nữ"],
            [{"noi_dung": f"Tổng chỉ tiêu năm 2026: {chi_tieu.get('tong_chi_tieu', 'chưa có')}", "nam": "", "nu": ""}],
        ),
        data,
        "chỉ tiêu",
    )


def _build_exam_context(query: str, data: dict) -> Optional[StructuredContext]:
    if not (
        "bài thi" in query
        or "vb2ca" in query
        or "ngưỡng đầu vào" in query
        or contains_any(query, ["ca1", "ca2", "ca3", "ca4", "ngày thi", "thời gian thi", "thi trên máy tính"])
    ):
        return None

    bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
    exam_items = bai_thi.get("cac_ma_bai_thi", [])

    if contains_any(query, ["ngưỡng đầu vào", "ngày thi", "thời gian thi", "thi trên máy tính"]):
        return build_table_context(
            "THÔNG TIN BÀI THI ĐÁNH GIÁ",
            ["Mục", "Chi tiết"],
            [
                {"muc": "Ngày thi", "chi_tiet": bai_thi.get("ngay_thi", "")},
                {"muc": "Thời gian làm bài", "chi_tiet": bai_thi.get("thoi_gian_lam_bai", "")},
                {"muc": "Hình thức thi", "chi_tiet": bai_thi.get("hinh_thuc_thi", "")},
                {"muc": "Địa điểm thi", "chi_tiet": bai_thi.get("dia_diem_thi", "")},
                {"muc": "Ngưỡng đầu vào", "chi_tiet": bai_thi.get("nguong_dau_vao", "")},
                {"muc": "Công thức tính điểm", "chi_tiet": bai_thi.get("cong_thuc_tinh_diem", "")},
            ],
            empty_message="Chưa có dữ liệu bài thi đánh giá.",
        )

    if "vb2ca" in query or "bài thi" in query or contains_any(query, ["ca1", "ca2", "ca3", "ca4"]):
        documents = build_vb2ca_exam_documents(exam_items)
        if documents:
            return build_document_collection_context(
                "BÀI THI ĐÁNH GIÁ",
                description="Danh sách 4 đề thi VB2CA. Có thể xem nhanh PDF hoặc tải file về máy.",
                documents=documents,
            )

    rows = [
        {
            "ma": item.get("ma", ""),
            "tu_luan_bat_buoc": item.get("tu_luan_bat_buoc", ""),
            "trac_nghiem_bat_buoc": ", ".join(item.get("trac_nghiem_bat_buoc", [])),
            "trac_nghiem_tu_chon": item.get("trac_nghiem_tu_chon", ""),
        }
        for item in exam_items
    ]
    return build_table_context(
        "BÀI THI ĐÁNH GIÁ",
        ["Mã", "Tự luận bắt buộc", "Trắc nghiệm bắt buộc", "Môn tự chọn"],
        rows,
        empty_message="Chưa có dữ liệu bài thi đánh giá.",
    )


def _build_major_context(query: str, ts: dict) -> Optional[StructuredContext]:
    if not ("ngành" in query or "tổ hợp" in query or "mã ngành" in query):
        return None

    if "được phép" in query or "ngành được" in query:
        return build_list_context(
            "NGÀNH ĐƯỢC PHÉP ĐĂNG KÝ",
            ts.get("nganh_duoc_phep_dang_ky", []),
            empty_message="Chưa có dữ liệu ngành được phép đăng ký.",
        )

    return build_table_context(
        "NGÀNH TUYỂN SINH",
        ["Tên ngành", "Mã ngành", "Mã trường", "Địa bàn", "Tổ hợp xét tuyển", "Mã bài thi"],
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


def _build_contact_context(query: str, data: dict) -> Optional[StructuredContext]:
    thong_tin = data.get("thong_tin_chung", {})

    if "mã trường" in query or "css" in query or "trường" in query:
        dia_chi = thong_tin.get("dia_chi", {})
        rows = [
            {"muc": "Tên trường", "chi_tiet": thong_tin.get("ten_truong_vi", "")},
            {"muc": "Tên tiếng Anh", "chi_tiet": thong_tin.get("ten_truong_en", "")},
            {"muc": "Mã trường", "chi_tiet": thong_tin.get("ma_truong", "")},
            {"muc": "Website", "chi_tiet": thong_tin.get("website", "")},
            {"muc": "Email tuyển sinh", "chi_tiet": thong_tin.get("email_tuyen_sinh", "")},
            {"muc": "Trụ sở chính", "chi_tiet": dia_chi.get("tru_so_chinh", "")},
            {"muc": "Cơ sở 2", "chi_tiet": dia_chi.get("co_so_2", "")},
            {"muc": "Cơ sở 3", "chi_tiet": dia_chi.get("co_so_3", "")},
        ]
        rows.extend(
            {"muc": f"Liên hệ tuyển sinh - {item.get('ho_ten', '')}", "chi_tiet": item.get("so_dien_thoai", "")}
            for item in thong_tin.get("lien_he_tuyen_sinh", [])
        )
        return build_table_context("THÔNG TIN TRƯỜNG", ["Mục", "Chi tiết"], rows)

    if "email" in query or "mail" in query or "liên hệ" in query:
        rows = [
            {"muc": "Website", "chi_tiet": thong_tin.get("website", "")},
            {"muc": "Email tuyển sinh", "chi_tiet": thong_tin.get("email_tuyen_sinh", "")},
        ]
        rows.extend(
            {"muc": item.get("ho_ten", ""), "chi_tiet": item.get("so_dien_thoai", "")}
            for item in thong_tin.get("lien_he_tuyen_sinh", [])
        )
        return build_table_context(
            "LIÊN HỆ TUYỂN SINH",
            ["Mục", "Chi tiết"],
            rows,
            empty_message="Chưa có dữ liệu liên hệ tuyển sinh.",
        )

    return None


def build_admission_context(query: str) -> Optional[StructuredContext]:
    query = normalize_admission_query(query)
    if not contains_any(query, ADMISSION_KEYWORDS):
        return None

    data = load_data("tuyen_sinh.json")
    if not data:
        return build_text_context("TUYỂN SINH", "Không thể tải dữ liệu tuyển sinh.")

    ts = data.get("tuyen_sinh_dai_hoc_chinh_quy", {})

    direct_context = (
        _build_conflict_context(data) if contains_any(query, ["liên thông", "lien thong"]) else None
    ) or (
        build_precheck_context(query, data, ts) if has_profile_signals(query) else None
    ) or _build_professional_context(query, data, ts) or _build_notice_context(query, data)
    if direct_context:
        return direct_context

    for builder in (
        lambda: _build_procedure_context(query, ts),
        lambda: _build_policy_context(query, ts),
        lambda: _build_score_context(query, ts),
        lambda: build_table_context(
            "TUYỂN SINH VĂN BẰNG 2",
            ["Mục", "Chi tiết"],
            build_vb2ca_overview_rows(data, ts),
            empty_message="Chưa có dữ liệu tuyển sinh văn bằng 2.",
        )
        if is_vb2_overview_query(query)
        else None,
        lambda: _build_quota_context(query, data, ts),
        lambda: build_table_context(
            "TUYỂN SINH",
            ["Mã", "Tên phương thức", "Mô tả"],
            [
                {"ma": item.get("ma", ""), "ten": item.get("ten", ""), "mo_ta": item.get("mo_ta", "")}
                for item in ts.get("phuong_thuc_tuyen_sinh", [])
            ],
            empty_message="Chưa có dữ liệu phương thức tuyển sinh.",
        )
        if "phương thức" in query or "xét tuyển" in query
        else None,
        lambda: build_list_context(
            "TIÊU CHUẨN SỨC KHỎE",
            ts.get("tieu_chuan_suc_khoe", []),
            empty_message="Chưa có dữ liệu tiêu chuẩn sức khỏe.",
        )
        if "sức khỏe" in query or contains_any(query, ["chiều cao", "bmi", "thị lực"])
        else None,
        lambda: build_list_context(
            "TUYỂN SINH",
            [*ts.get("doi_tuong_du_tuyen", []), *ts.get("dieu_kien_chung", [])],
            empty_message="Chưa có dữ liệu điều kiện dự tuyển.",
        )
        if "điều kiện" in query or "lý lịch" in query or "đối tượng" in query or "tuổi" in query
        else None,
        lambda: _build_exam_context(query, data),
        lambda: build_list_context(
            "HỒ SƠ TUYỂN SINH",
            ts.get("ho_so_nhap_hoc", []),
            empty_message="Chưa có dữ liệu hồ sơ tuyển sinh.",
        )
        if "hồ sơ" in query or "nhập học" in query
        else None,
        lambda: _build_major_context(query, ts),
        lambda: _build_contact_context(query, data),
    ):
        result = builder()
        if result:
            return result

    return build_text_context(
        "TUYỂN SINH",
        (
            "Bạn hãy hỏi cụ thể hơn về tuyển sinh như chỉ tiêu, "
            "phương thức, điều kiện, chứng chỉ, bài thi VB2CA, hồ sơ hoặc ngành tuyển sinh."
        ),
    )
