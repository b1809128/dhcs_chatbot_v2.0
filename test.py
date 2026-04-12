# Quản lý thẻ xe
    # if any(k in q for k in ["thẻ xe", "biển số", "xe", "đăng ký gửi xe", "gia hạn"]):
    #     data = load_data("the_xe.json")
    #     if data:
    #         context_parts.append("=== QUẢN LÝ THẺ XE ===\n" +
    #                              json.dumps(data, ensure_ascii=False, indent=2))

    # Ra vào buổi chiều / ngày nghỉ
    # if any(k in q for k in ["ra vào", "buổi chiều", "ngày nghỉ", "thời gian ra", "điểm danh"]):
    #     data = load_data("ra_vao.json")
    #     if data:
    #         context_parts.append("=== QUẢN LÝ RA VÀO ===\n" +
    #                              json.dumps(data, ensure_ascii=False, indent=2))

import json
from typing import Optional, List, Dict, Any


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def find_first_matching_item(items: List[Dict[str, Any]], q: str, field: str) -> Optional[Dict[str, Any]]:
    for item in items:
        value = str(item.get(field, "")).lower()
        if value and value in q:
            return item
    return None


def build_schedule_context(q: str) -> Optional[str]:
    keywords = [
        "lịch học", "lịch thi", "phòng", "lớp",
        "học hôm nay", "thi khi nào",
        "dths3", "thahs", "qlhc", "kths"
    ]

    if not contains_any(q, keywords):
        return None

    data = load_data("lich_hoc.json")
    if not data:
        return None

    lich_hoc = data.get("lich_hoc", [])
    lich_thi = data.get("lich_thi", [])

    # Hỏi lịch thi
    if "lịch thi" in q or "thi khi nào" in q:
        lines = ["=== LỊCH THI ==="]
        if not lich_thi:
            lines.append("Hiện chưa có dữ liệu lịch thi.")
            return "\n".join(lines)

        matched = False
        for item in lich_thi:
            mon = item.get("mon", "").lower()
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
    lines = ["=== LỊCH HỌC ==="]

    matched_class = False
    for item in lich_hoc:
        lop = item.get("lop", "").lower()
        mon = item.get("mon", "").lower()

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


def build_document_context(q: str) -> Optional[str]:
    keywords = [
        "công văn", "thông tư", "nghị định",
        "đảng viên", "đoàn thanh niên",
        "đơn", "đơn xin phép", "đơn nghỉ", "tranh thủ"
    ]

    if not contains_any(q, keywords):
        return None

    data = load_data("ho_so.json")
    if not data:
        return None

    lines = ["=== CÔNG VĂN / THÔNG TƯ / BIỂU MẪU ==="]

    if "công văn" in q:
        items = data.get("cong_van", [])
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
        items = data.get("thong_tu", [])
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
        items = data.get("nghi_dinh", [])
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
        items = data.get("bieu_mau", [])
        if not items:
            return "=== BIỂU MẪU ===\nHiện chưa có dữ liệu biểu mẫu."

        lines[0] = "=== BIỂU MẪU / ĐƠN ==="
        matched = False

        for item in items:
            ten = item.get("ten", "").lower()
            if ten and ten in q:
                matched = True
                lines.append(f"Tên biểu mẫu: {item.get('ten', '')}")
                lines.append(f"- Mô tả: {item.get('mo_ta', '')}")
                lines.append(f"- Nội dung mẫu: {item.get('noi_dung_mau', '')}")
                break

        if not matched:
            lines.append("Các biểu mẫu hiện có:")
            for item in items:
                lines.append(f"- {item.get('ten', '')}: {item.get('mo_ta', '')}")

        return "\n".join(lines)

    if "đoàn" in q or "đảng" in q:
        items = data.get("to_chuc", [])
        if not items:
            return "=== TỔ CHỨC ===\nHiện chưa có dữ liệu tổ chức."

        lines[0] = "=== TỔ CHỨC ==="
        lines.append("Thông tin tổ chức liên quan:")
        for item in items:
            lines.append(f"- {item.get('ten', '')}: {item.get('noi_dung', '')}")
        return "\n".join(lines)

    return None


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

    data = load_data("tai_lieu.json")
    if not data:
        return None

    lines = ["=== TÀI LIỆU NGHIỆP VỤ ==="]
    lines.append(f"Mô tả: {data.get('mo_ta', '')}")
    lines.append("")

    # Nếu user hỏi ôn tập
    if contains_any(q, ["ôn", "ôn tập", "luyện", "câu hỏi", "trắc nghiệm"]):
        lines.append("Nội dung hỗ trợ ôn tập:")
        for item in data.get("chuc_nang", []):
            ten = item.get("ten", "").lower()
            if "ôn" in ten or "câu hỏi" in ten or "học" in ten:
                lines.append(f"- {item.get('ten', '')}:")
                for nd in item.get("noi_dung", []):
                    lines.append(f"  + {nd}")
        lines.append("")

    # Nếu user hỏi giải thích / không hiểu bài
    elif contains_any(q, ["giải thích", "không hiểu", "giảng lại", "hiểu bài"]):
        lines.append("Nội dung hỗ trợ giải thích bài học:")
        for item in data.get("chuc_nang", []):
            ten = item.get("ten", "").lower()
            if "giải thích" in ten or "giải đáp" in ten:
                lines.append(f"- {item.get('ten', '')}:")
                for nd in item.get("noi_dung", []):
                    lines.append(f"  + {nd}")
        lines.append("")

    # Nếu user hỏi tóm tắt
    elif contains_any(q, ["tóm tắt", "tóm lược", "ghi nhớ", "ý chính"]):
        lines.append("Nội dung hỗ trợ tóm tắt giáo trình:")
        for item in data.get("chuc_nang", []):
            ten = item.get("ten", "").lower()
            if "tóm tắt" in ten:
                lines.append(f"- {item.get('ten', '')}:")
                for nd in item.get("noi_dung", []):
                    lines.append(f"  + {nd}")
        lines.append("")

    else:
        lines.append("Các chức năng hỗ trợ học tập:")
        for item in data.get("chuc_nang", []):
            lines.append(f"- {item.get('ten', '')}:")
            for nd in item.get("noi_dung", []):
                lines.append(f"  + {nd}")
            lines.append("")

    lines.append("Lĩnh vực áp dụng:")
    for lv in data.get("linh_vuc", []):
        lines.append(f"- {lv}")

    return "\n".join(lines)


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

    data = load_data("thu_vien.json")
    if not data:
        return None

    books = data.get("thu_vien", [])
    lines = ["=== THÔNG TIN THƯ VIỆN ==="]

    # Tìm theo tên sách
    matched_books = []
    for book in books:
        ten_sach = book.get("ten_sach", "").lower()
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

    # Hỏi sách còn / hết
    if "còn sách" in q or "còn không" in q:
        lines.append("Các sách hiện còn trong thư viện:")
        for book in books:
            if book.get("so_luong", 0) > 0:
                lines.append(
                    f"- {book.get('ten_sach', '')}: {book.get('so_luong', 0)} cuốn, "
                    f"kệ {book.get('ke_sach', '')}, mượn {book.get('thoi_gian_muon', '')}"
                )
        return "\n".join(lines)

    if "hết sách" in q or "hết chưa" in q:
        lines.append("Các sách hiện đã hết:")
        for book in books:
            if book.get("so_luong", 0) == 0:
                lines.append(f"- {book.get('ten_sach', '')}: kệ {book.get('ke_sach', '')}")
        return "\n".join(lines)

    # Hỏi chung
    lines.append("Một số sách hiện có trong thư viện:")
    for book in books:
        lines.append(
            f"- {book.get('ten_sach', '')}: {book.get('tinh_trang', '')}, "
            f"kệ {book.get('ke_sach', '')}, mượn {book.get('thoi_gian_muon', '')}"
        )

    return "\n".join(lines)