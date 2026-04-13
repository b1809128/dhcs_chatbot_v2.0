import os
import requests
import pymysql

from flask import Flask, request, jsonify, render_template
from typing import Optional, List, Dict, Any


app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2:1.5b"

# =========================
# MYSQL CONFIG
# =========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          # sửa mật khẩu MySQL của bạn
    "database": "chatbot_ppu",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


# =========================
# DB HELPERS
# =========================
def get_connection():
    return pymysql.connect(**DB_CONFIG)


def fetch_all(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


# =========================
# SCHEDULE CONTEXT
# Bảng gợi ý:
# - lich_hoc(id, lop, mon, giang_vien, phong, thoi_gian)
# - lich_thi(id, mon, ngay_thi, phong)
# =========================
def build_schedule_context(q: str) -> Optional[str]:
    keywords = [
        "lịch học", "lịch thi", "phòng", "lớp",
        "học hôm nay", "thi khi nào",
        "dths3", "thahs", "qlhc", "kths"
    ]

    if not contains_any(q, keywords):
        return None

    # Hỏi lịch thi
    if "lịch thi" in q or "thi khi nào" in q:
        lich_thi = fetch_all("""
            SELECT mon, ngay_thi, phong
            FROM lich_thi
            ORDER BY ngay_thi ASC
        """)

        lines = ["=== LỊCH THI ==="]

        if not lich_thi:
            lines.append("Hiện chưa có dữ liệu lịch thi.")
            return "\n".join(lines)

        matched = False
        for item in lich_thi:
            mon = str(item.get("mon", "")).lower()
            if mon and mon in q:
                matched = True
                lines.append(f"Môn thi: {item.get('mon', '')}")
                lines.append(f"- Ngày thi: {item.get('ngay_thi', '')}")
                lines.append(f"- Phòng thi: {item.get('phong', '')}")
                break

        if not matched:
            lines.append("Các môn có trong lịch thi:")
            for item in lich_thi:
                lines.append(
                    f"- {item.get('mon', '')}: {item.get('ngay_thi', '')} tại {item.get('phong', '')}"
                )

        return "\n".join(lines)

    # Hỏi lịch học
    lich_hoc = fetch_all("""
        SELECT lop, mon, giang_vien, phong, thoi_gian
        FROM lich_hoc
        ORDER BY lop ASC, thoi_gian ASC
    """)

    if not lich_hoc:
        return "=== LỊCH HỌC ===\nHiện chưa có dữ liệu lịch học."

    lines = ["=== LỊCH HỌC ==="]
    matched_class = False

    for item in lich_hoc:
        lop = str(item.get("lop", "")).lower()
        mon = str(item.get("mon", "")).lower()

        if (lop and lop in q) or (mon and mon in q):
            matched_class = True
            lines.append(f"Lớp: {item.get('lop', '')}")
            lines.append(f"- Môn: {item.get('mon', '')}")
            lines.append(f"- Giảng viên: {item.get('giang_vien', '')}")
            lines.append(f"- Phòng: {item.get('phong', '')}")
            lines.append(f"- Thời gian: {item.get('thoi_gian', '')}")
            lines.append("")

    if not matched_class:
        lines.append("Các lớp hiện có trong lịch học:")
        for item in lich_hoc:
            lines.append(
                f"- {item.get('lop', '')}: {item.get('mon', '')}, "
                f"{item.get('thoi_gian', '')}, phòng {item.get('phong', '')}"
            )

    return "\n".join(lines)


# =========================
# DOCUMENT CONTEXT
# Bảng gợi ý:
# - cong_van(id, ten, so_hieu, ngay_ban_hanh, noi_dung, doi_tuong, trang_thai)
# - thong_tu(id, ten, so_hieu, ngay_ban_hanh, noi_dung, trang_thai)
# - nghi_dinh(id, ten, so_hieu, ngay_ban_hanh, noi_dung, trang_thai)
# - bieu_mau(id, ten, mo_ta, noi_dung_mau)
# - to_chuc(id, ten, noi_dung)
# =========================
def build_document_context(q: str) -> Optional[str]:
    keywords = [
        "công văn", "thông tư", "nghị định",
        "đảng viên", "đoàn thanh niên",
        "đơn", "đơn xin phép", "đơn nghỉ", "tranh thủ"
    ]

    if not contains_any(q, keywords):
        return None

    lines = ["=== CÔNG VĂN / THÔNG TƯ / BIỂU MẪU ==="]

    if "công văn" in q:
        items = fetch_all("""
            SELECT ten, so_hieu, ngay_ban_hanh, noi_dung, doi_tuong, trang_thai
            FROM cong_van
            ORDER BY ngay_ban_hanh DESC
        """)

        if not items:
            return "=== CÔNG VĂN ===\nHiện chưa có dữ liệu công văn."

        lines[0] = "=== CÔNG VĂN ==="
        lines.append("Thông tin công văn liên quan:")
        for item in items:
            lines.append(f"- Tên: {item.get('ten', '')}")
            lines.append(f"  Số hiệu: {item.get('so_hieu', '')}")
            lines.append(f"  Ngày ban hành: {item.get('ngay_ban_hanh', '')}")
            lines.append(f"  Nội dung: {item.get('noi_dung', '')}")
            lines.append(f"  Đối tượng: {item.get('doi_tuong', '')}")
            lines.append(f"  Trạng thái: {item.get('trang_thai', '')}")
            lines.append("")
        return "\n".join(lines)

    if "thông tư" in q:
        items = fetch_all("""
            SELECT ten, so_hieu, ngay_ban_hanh, noi_dung, trang_thai
            FROM thong_tu
            ORDER BY ngay_ban_hanh DESC
        """)

        if not items:
            return "=== THÔNG TƯ ===\nHiện chưa có dữ liệu thông tư."

        lines[0] = "=== THÔNG TƯ ==="
        lines.append("Thông tin thông tư liên quan:")
        for item in items:
            lines.append(f"- Tên: {item.get('ten', '')}")
            lines.append(f"  Số hiệu: {item.get('so_hieu', '')}")
            lines.append(f"  Ngày ban hành: {item.get('ngay_ban_hanh', '')}")
            lines.append(f"  Nội dung: {item.get('noi_dung', '')}")
            lines.append(f"  Trạng thái: {item.get('trang_thai', '')}")
            lines.append("")
        return "\n".join(lines)

    if "nghị định" in q:
        items = fetch_all("""
            SELECT ten, so_hieu, ngay_ban_hanh, noi_dung, trang_thai
            FROM nghi_dinh
            ORDER BY ngay_ban_hanh DESC
        """)

        if not items:
            return "=== NGHỊ ĐỊNH ===\nHiện chưa có dữ liệu nghị định."

        lines[0] = "=== NGHỊ ĐỊNH ==="
        lines.append("Thông tin nghị định liên quan:")
        for item in items:
            lines.append(f"- Tên: {item.get('ten', '')}")
            lines.append(f"  Số hiệu: {item.get('so_hieu', '')}")
            lines.append(f"  Ngày ban hành: {item.get('ngay_ban_hanh', '')}")
            lines.append(f"  Nội dung: {item.get('noi_dung', '')}")
            lines.append(f"  Trạng thái: {item.get('trang_thai', '')}")
            lines.append("")
        return "\n".join(lines)

    if "đơn" in q:
        items = fetch_all("""
            SELECT ten, mo_ta, noi_dung_mau
            FROM bieu_mau
            ORDER BY ten ASC
        """)

        if not items:
            return "=== BIỂU MẪU ===\nHiện chưa có dữ liệu biểu mẫu."

        lines[0] = "=== BIỂU MẪU / ĐƠN ==="
        matched = False

        for item in items:
            ten = str(item.get("ten", "")).lower()
            if ten and ten in q:
                matched = True
                lines.append(f"Tên biểu mẫu: {item.get('ten', '')}")
                lines.append(f"- Mô tả: {item.get('mo_ta', '')}")
                lines.append(f"- Nội dung mẫu: {item.get('noi_dung_mau', '')}")
                break

        if not matched:
            lines.append("Các biểu mẫu hiện có:")
            for item in items:
                lines.append(
                    f"- {item.get('ten', '')}: {item.get('mo_ta', '')}")

        return "\n".join(lines)

    if "đoàn" in q or "đảng" in q:
        items = fetch_all("""
            SELECT ten, noi_dung
            FROM to_chuc
            ORDER BY ten ASC
        """)

        if not items:
            return "=== TỔ CHỨC ===\nHiện chưa có dữ liệu tổ chức."

        lines[0] = "=== TỔ CHỨC ==="
        lines.append("Thông tin tổ chức liên quan:")
        for item in items:
            lines.append(
                f"- {item.get('ten', '')}: {item.get('noi_dung', '')}")
        return "\n".join(lines)

    return None


# =========================
# STUDY MATERIAL CONTEXT
# Bảng gợi ý:
# - tai_lieu_meta(id, mo_ta)
# - tai_lieu_chuc_nang(id, ten)
# - tai_lieu_noi_dung(id, chuc_nang_id, noi_dung)
# - tai_lieu_linh_vuc(id, ten)
# =========================
def build_study_material_context(q: str) -> Optional[str]:
    keywords = [
        "học", "bài", "môn", "kiến thức",
        "tài liệu", "giáo trình", "file", "pdf",
        "giải thích", "không hiểu", "giảng lại", "hiểu bài",
        "ôn", "ôn tập", "luyện", "câu hỏi", "trắc nghiệm",
        "tóm tắt", "tóm lược", "ghi nhớ", "ý chính",
        "luật", "hình sự", "hành chính", "tố tụng", "nghiệp vụ"
    ]

    if not contains_any(q, keywords):
        return None

    meta = fetch_all("SELECT mo_ta FROM tai_lieu_meta LIMIT 1")
    chuc_nang = fetch_all(
        "SELECT id, ten FROM tai_lieu_chuc_nang ORDER BY id ASC")
    linh_vuc = fetch_all("SELECT ten FROM tai_lieu_linh_vuc ORDER BY id ASC")

    if not chuc_nang:
        return None

    lines = ["=== TÀI LIỆU NGHIỆP VỤ ==="]
    lines.append(f"Mô tả: {meta[0]['mo_ta'] if meta else ''}")
    lines.append("")

    def get_noi_dung_by_chuc_nang(chuc_nang_id: int) -> List[Dict[str, Any]]:
        return fetch_all(
            "SELECT noi_dung FROM tai_lieu_noi_dung WHERE chuc_nang_id = %s ORDER BY id ASC",
            (chuc_nang_id,)
        )

    if contains_any(q, ["ôn", "ôn tập", "luyện", "câu hỏi", "trắc nghiệm"]):
        lines.append("Nội dung hỗ trợ ôn tập:")
        for item in chuc_nang:
            ten = str(item.get("ten", "")).lower()
            if "ôn" in ten or "câu hỏi" in ten or "học" in ten:
                lines.append(f"- {item.get('ten', '')}:")
                for nd in get_noi_dung_by_chuc_nang(item["id"]):
                    lines.append(f"  + {nd.get('noi_dung', '')}")
        lines.append("")

    elif contains_any(q, ["giải thích", "không hiểu", "giảng lại", "hiểu bài"]):
        lines.append("Nội dung hỗ trợ giải thích bài học:")
        for item in chuc_nang:
            ten = str(item.get("ten", "")).lower()
            if "giải thích" in ten or "giải đáp" in ten:
                lines.append(f"- {item.get('ten', '')}:")
                for nd in get_noi_dung_by_chuc_nang(item["id"]):
                    lines.append(f"  + {nd.get('noi_dung', '')}")
        lines.append("")

    elif contains_any(q, ["tóm tắt", "tóm lược", "ghi nhớ", "ý chính"]):
        lines.append("Nội dung hỗ trợ tóm tắt giáo trình:")
        for item in chuc_nang:
            ten = str(item.get("ten", "")).lower()
            if "tóm tắt" in ten:
                lines.append(f"- {item.get('ten', '')}:")
                for nd in get_noi_dung_by_chuc_nang(item["id"]):
                    lines.append(f"  + {nd.get('noi_dung', '')}")
        lines.append("")

    else:
        lines.append("Các chức năng hỗ trợ học tập:")
        for item in chuc_nang:
            lines.append(f"- {item.get('ten', '')}:")
            for nd in get_noi_dung_by_chuc_nang(item["id"]):
                lines.append(f"  + {nd.get('noi_dung', '')}")
            lines.append("")

    lines.append("Lĩnh vực áp dụng:")
    for lv in linh_vuc:
        lines.append(f"- {lv.get('ten', '')}")

    return "\n".join(lines)


# =========================
# LIBRARY CONTEXT
# Bảng gợi ý:
# - thu_vien(id, ten_sach, so_luong, ke_sach, tinh_trang, thoi_gian_muon)
# =========================
def build_library_context(q: str) -> Optional[str]:
    keywords = [
        "sách", "thư viện", "mượn",
        "tìm sách", "có sách", "còn sách", "hết sách",
        "ở đâu", "kệ", "vị trí",
        "mượn bao lâu", "thời gian mượn",
        "luật", "hình sự", "tố tụng", "hành chính", "nghiệp vụ"
    ]

    if not contains_any(q, keywords):
        return None

    books = fetch_all("""
        SELECT ten_sach, so_luong, ke_sach, tinh_trang, thoi_gian_muon
        FROM thu_vien
        ORDER BY ten_sach ASC
    """)

    if not books:
        return "=== THÔNG TIN THƯ VIỆN ===\nHiện chưa có dữ liệu thư viện."

    lines = ["=== THÔNG TIN THƯ VIỆN ==="]

    matched_books = []
    for book in books:
        ten_sach = str(book.get("ten_sach", "")).lower()
        if ten_sach and ten_sach in q:
            matched_books.append(book)

    if matched_books:
        for book in matched_books:
            lines.append(f"Tên sách: {book.get('ten_sach', '')}")
            lines.append(f"- Số lượng: {book.get('so_luong', 0)}")
            lines.append(f"- Vị trí kệ: {book.get('ke_sach', '')}")
            lines.append(f"- Tình trạng: {book.get('tinh_trang', '')}")
            lines.append(f"- Thời gian mượn: {book.get('thoi_gian_muon', '')}")
            lines.append("")
        return "\n".join(lines)

    if "còn sách" in q or "còn không" in q:
        lines.append("Các sách hiện còn trong thư viện:")
        for book in books:
            if int(book.get("so_luong", 0)) > 0:
                lines.append(
                    f"- {book.get('ten_sach', '')}: {book.get('so_luong', 0)} cuốn, "
                    f"kệ {book.get('ke_sach', '')}, mượn {book.get('thoi_gian_muon', '')}"
                )
        return "\n".join(lines)

    if "hết sách" in q or "hết chưa" in q:
        lines.append("Các sách hiện đã hết:")
        for book in books:
            if int(book.get("so_luong", 0)) == 0:
                lines.append(
                    f"- {book.get('ten_sach', '')}: kệ {book.get('ke_sach', '')}")
        return "\n".join(lines)

    lines.append("Một số sách hiện có trong thư viện:")
    for book in books:
        lines.append(
            f"- {book.get('ten_sach', '')}: {book.get('tinh_trang', '')}, "
            f"kệ {book.get('ke_sach', '')}, mượn {book.get('thoi_gian_muon', '')}"
        )

    return "\n".join(lines)


# =========================
# ADMISSION CONTEXT
# Bảng gợi ý:
# - tuyen_sinh_meta
# - tuyen_sinh_chi_tieu
# - tuyen_sinh_phuong_thuc
# - tuyen_sinh_dieu_kien_chung
# - tuyen_sinh_pt2_yeu_cau
# - tuyen_sinh_chung_chi
# - bai_thi_meta
# - bai_thi_ma
# - nganh_tuyen_sinh
# - lien_he_tuyen_sinh
# =========================
def build_admission_context(q: str) -> Optional[str]:
    keywords = [
        "tuyển sinh", "chính quy", "văn bằng 2", "liên thông", "thạc sĩ",
        "nghiên cứu sinh", "vừa học vừa làm", "sức khỏe", "tiếng anh",
        "chứng chỉ", "lý lịch", "ngành", "thông báo tuyển",
        "chỉ tiêu", "phương thức", "xét tuyển", "bài thi",
        "ca1", "ca2", "ca3", "ca4", "tổ hợp", "mã trường", "mã ngành"
    ]

    if not contains_any(q, keywords):
        return None

    reply = ""

    if "chỉ tiêu" in q:
        rows = fetch_all("SELECT * FROM tuyen_sinh_chi_tieu LIMIT 1")
        if not rows:
            return "Chưa có dữ liệu chỉ tiêu tuyển sinh."
        row = rows[0]
        reply = (
            f"Chỉ tiêu tuyển sinh năm 2026 là {row.get('tong_chi_tieu', 'chưa có')} chỉ tiêu.\n"
            f"- Phương thức 1: {row.get('pt1_nam', 0)} nam, {row.get('pt1_nu', 0)} nữ.\n"
            f"- Phương thức 2 và 3: {row.get('pt23_nam', 0)} nam, {row.get('pt23_nu', 0)} nữ."
        )

    elif "phương thức" in q or "xét tuyển" in q:
        pts = fetch_all(
            "SELECT ma, ten, mo_ta FROM tuyen_sinh_phuong_thuc ORDER BY ma ASC")
        if not pts:
            return "Chưa có dữ liệu phương thức tuyển sinh."

        reply = "Nhà trường áp dụng các phương thức tuyển sinh sau:\n"
        for pt in pts:
            reply += f"- Phương thức {pt.get('ma', '')}: {pt.get('ten', '')}.\n"
            reply += f"  Mô tả: {pt.get('mo_ta', '')}\n"

    elif "điều kiện" in q or "lý lịch" in q or "sức khỏe" in q:
        dieu_kien = fetch_all(
            "SELECT noi_dung FROM tuyen_sinh_dieu_kien_chung ORDER BY id ASC")
        if not dieu_kien:
            return "Chưa có dữ liệu điều kiện tuyển sinh."

        reply = "Điều kiện dự tuyển gồm:\n"
        for dk in dieu_kien:
            reply += f"- {dk.get('noi_dung', '')}\n"

    elif "chứng chỉ" in q or "tiếng anh" in q or "ielts" in q:
        yeu_cau = fetch_all(
            "SELECT noi_dung FROM tuyen_sinh_pt2_yeu_cau ORDER BY id ASC")
        cc = fetch_all(
            "SELECT ten_chung_chi, muc_yeu_cau FROM tuyen_sinh_chung_chi ORDER BY id ASC")

        reply = "Điều kiện về chứng chỉ ngoại ngữ đối với phương thức 2 như sau:\n"
        for item in yeu_cau:
            reply += f"- {item.get('noi_dung', '')}\n"

        reply += "\nMột số mức chứng chỉ được chấp nhận:\n"
        for item in cc:
            reply += f"- {item.get('ten_chung_chi', '')}: {item.get('muc_yeu_cau', '')}\n"

    elif "bài thi" in q or contains_any(q, ["ca1", "ca2", "ca3", "ca4"]):
        meta_rows = fetch_all("SELECT * FROM bai_thi_meta LIMIT 1")
        cac_ma = fetch_all("""
            SELECT ma, tu_luan_bat_buoc, trac_nghiem_bat_buoc, trac_nghiem_tu_chon
            FROM bai_thi_ma
            ORDER BY ma ASC
        """)

        if not meta_rows:
            return "Chưa có dữ liệu bài thi đánh giá."

        meta = meta_rows[0]
        reply = (
            f"Bài thi đánh giá của Bộ Công an có {meta.get('tong_so_ma_bai_thi', '')} mã bài thi, "
            f"hình thức {meta.get('hinh_thuc_thi', '')}, "
            f"thời gian làm bài {meta.get('thoi_gian_lam_bai', '')}, "
            f"ngày thi {meta.get('ngay_thi', '')}.\n"
        )

        reply += "\nChi tiết các mã bài thi:\n"
        for item in cac_ma:
            reply += f"- {item.get('ma', '')}: "
            reply += f"tự luận {item.get('tu_luan_bat_buoc', '')}; "
            reply += f"trắc nghiệm bắt buộc gồm {item.get('trac_nghiem_bat_buoc', '')}; "
            reply += f"môn tự chọn là {item.get('trac_nghiem_tu_chon', '')}.\n"

    elif "ngành" in q or "tổ hợp" in q or "mã ngành" in q:
        nganh_list = fetch_all("""
            SELECT ten_nganh, ma_nganh, ma_truong, dia_ban, to_hop_xet_tuyen_pt3, ma_bai_thi_danh_gia
            FROM nganh_tuyen_sinh
            ORDER BY ten_nganh ASC
        """)

        if not nganh_list:
            return "Chưa có dữ liệu ngành tuyển sinh."

        reply = "Thông tin ngành tuyển sinh như sau:\n"
        for nganh in nganh_list:
            reply += f"- Tên ngành: {nganh.get('ten_nganh', '')}\n"
            reply += f"  Mã ngành: {nganh.get('ma_nganh', '')}\n"
            reply += f"  Mã trường: {nganh.get('ma_truong', '')}\n"
            reply += f"  Địa bàn tuyển sinh: {nganh.get('dia_ban', '')}\n"
            reply += f"  Tổ hợp xét tuyển: {nganh.get('to_hop_xet_tuyen_pt3', '')}\n"
            reply += f"  Mã bài thi đánh giá: {nganh.get('ma_bai_thi_danh_gia', '')}\n"

    elif "mã trường" in q or "css" in q or "trường" in q:
        tt_rows = fetch_all("SELECT * FROM tuyen_sinh_meta LIMIT 1")
        lien_he = fetch_all(
            "SELECT ho_ten, so_dien_thoai FROM lien_he_tuyen_sinh ORDER BY id ASC")

        if not tt_rows:
            return "Chưa có dữ liệu thông tin chung tuyển sinh."

        tt = tt_rows[0]
        reply = (
            f"Thông tin chung của trường:\n"
            f"- Tên trường: {tt.get('ten_truong_vi', '')}\n"
            f"- Tên tiếng Anh: {tt.get('ten_truong_en', '')}\n"
            f"- Mã trường: {tt.get('ma_truong', '')}\n"
            f"- Website: {tt.get('website', '')}\n"
            f"- Trụ sở chính: {tt.get('tru_so_chinh', '')}\n"
            f"- Cơ sở 2: {tt.get('co_so_2', '')}\n"
            f"- Cơ sở 3: {tt.get('co_so_3', '')}\n"
        )

        if lien_he:
            reply += "Liên hệ tuyển sinh:\n"
            for item in lien_he:
                reply += f"- {item.get('ho_ten', '')}: {item.get('so_dien_thoai', '')}\n"

    else:
        reply = (
            "Bạn hãy hỏi cụ thể hơn về tuyển sinh như chỉ tiêu, "
            "phương thức, điều kiện, chứng chỉ, bài thi hoặc ngành tuyển sinh."
        )

    return reply


# =========================
# BUILD FULL CONTEXT
# =========================
def build_context(query: str) -> Optional[str]:
    q = query.lower().strip()

    builders = [
        build_schedule_context,
        # build_document_context,
        # build_study_material_context,
        # build_library_context,
        # build_admission_context,
    ]

    context_parts = []
    for builder in builders:
        result = builder(q)
        if result:
            context_parts.append(result)

    if not context_parts:
        return None

    return "\n\n".join(context_parts)


# =========================
# OLLAMA
# =========================
def ask_ollama(question: str, context: str) -> str:
    system_prompt = (
        "Bạn là trợ lý hỗ trợ sinh viên trường Đại học Cảnh sát (ĐHCS). "
        "Chỉ trả lời dựa trên thông tin được cung cấp. "
        "Nếu không có thông tin, hãy nói 'Tôi chưa có thông tin về vấn đề này.' "
        "Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng."
    )

    if context:
        prompt = f"{system_prompt}\n\nThông tin nội bộ:\n{context}\n\nCâu hỏi: {question}\nTrả lời:"
    else:
        prompt = f"{system_prompt}\n\nCâu hỏi: {question}\nTrả lời:"

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 512}
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "❌ Không kết nối được Ollama. Hãy chắc chắn Ollama đang chạy (ollama serve)."
    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("message", "").strip()

    if not question:
        return jsonify({"reply": "Vui lòng nhập câu hỏi."})

    context = build_context(question)
    answer = ask_ollama(question, context)

    return jsonify({"reply": answer})


if __name__ == "__main__":
    print("🚀 Khởi động chatbot ĐHCS tại http://localhost:5000")
    app.run(debug=True, port=5000)
