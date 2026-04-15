from typing import Optional

from .keywords import ADMISSION_KEYWORDS
from .types import StructuredContext
from .utils import build_list_context, build_table_context, build_text_context, contains_any, load_data


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
        pt2 = chi_tieu.get("phuong_thuc_2", chi_tieu.get("phuong_thuc_2_3", {}))
        return build_table_context(
            "TUYỂN SINH",
            ["Nội dung", "Nam", "Nữ"],
            [
                {"noi_dung": f"Tổng chỉ tiêu năm 2026: {tong}", "nam": "", "nu": ""},
                {"noi_dung": "Phương thức 1", "nam": pt1.get("nam", 0), "nu": pt1.get("nu", 0)},
                {"noi_dung": "Phương thức 2", "nam": pt2.get("nam", 0), "nu": pt2.get("nu", 0)},
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
        rows = [{"loai": "Yêu cầu chung", "chi_tiet": yeu_cau} for yeu_cau in pt2.get("yeu_cau_chung", [])]
        rows.extend(
            {"loai": ten_chung_chi, "chi_tiet": muc}
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

    if "mã trường" in query or "css" in query or "trường" in query:
        thong_tin = data.get("thong_tin_chung", {})
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

    return build_text_context(
        "TUYỂN SINH",
        (
            "Bạn hãy hỏi cụ thể hơn về tuyển sinh như chỉ tiêu, "
            "phương thức, điều kiện, chứng chỉ, bài thi VB2CA, hồ sơ hoặc ngành tuyển sinh."
        ),
    )
