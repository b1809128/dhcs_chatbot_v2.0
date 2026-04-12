import json
import os
import requests
from flask import Flask, request, jsonify, render_template
from typing import Optional, List, Dict, Any


app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2:1.5b"  # hoặc "qwen2" nếu bạn dùng Qwen


def load_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def format_json_block(title: str, data) -> str:
    return f"{title}\n" + json.dumps(data, ensure_ascii=False, indent=2)


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

    data = load_data("tuyen_sinh.json")
    if not data:
        return "Không thể tải dữ liệu tuyển sinh."

    reply = ""
    ts = data.get("tuyen_sinh_dai_hoc_chinh_quy", {})

    if "chỉ tiêu" in q:
        chi_tieu = ts.get("chi_tieu", {})
        tong = chi_tieu.get("tong_chi_tieu", "chưa có")
        pt1 = chi_tieu.get("phuong_thuc_1", {})
        pt23 = chi_tieu.get("phuong_thuc_2_3", {})

        reply = (
            f"Chỉ tiêu tuyển sinh năm 2026 là {tong} chỉ tiêu.\n"
            f"- Phương thức 1: {pt1.get('nam', 0)} nam, {pt1.get('nu', 0)} nữ.\n"
            f"- Phương thức 2 và 3: {pt23.get('nam', 0)} nam, {pt23.get('nu', 0)} nữ."
        )

    elif "phương thức" in q or "xét tuyển" in q:
        pts = ts.get("phuong_thuc_tuyen_sinh", [])
        reply = "Nhà trường áp dụng các phương thức tuyển sinh sau:\n"
        for pt in pts:
            reply += f"- Phương thức {pt.get('ma', '')}: {pt.get('ten', '')}.\n"
            reply += f"  Mô tả: {pt.get('mo_ta', '')}\n"

    elif "điều kiện" in q or "lý lịch" in q or "sức khỏe" in q:
        dieu_kien = ts.get("dieu_kien_chung", [])
        reply = "Điều kiện dự tuyển gồm:\n"
        for dk in dieu_kien:
            reply += f"- {dk}\n"

    elif "chứng chỉ" in q or "tiếng anh" in q or "ielts" in q:
        pt2 = ts.get("dieu_kien_theo_phuong_thuc", {}).get("phuong_thuc_2", {})
        yeu_cau = pt2.get("yeu_cau_chung", [])
        cc = pt2.get("chung_chi_ngoai_ngu", {})

        reply = "Điều kiện về chứng chỉ ngoại ngữ đối với phương thức 2 như sau:\n"
        for item in yeu_cau:
            reply += f"- {item}\n"

        reply += "\nMột số mức chứng chỉ được chấp nhận:\n"
        for ten_cc, muc in cc.items():
            reply += f"- {ten_cc}: {muc}\n"

    elif "bài thi" in q or contains_any(q, ["ca1", "ca2", "ca3", "ca4"]):
        bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
        cac_ma = bai_thi.get("cac_ma_bai_thi", [])

        reply = (
            f"Bài thi đánh giá của Bộ Công an có {bai_thi.get('tong_so_ma_bai_thi', '')} mã bài thi, "
            f"hình thức {bai_thi.get('hinh_thuc_thi', '')}, "
            f"thời gian làm bài {bai_thi.get('thoi_gian_lam_bai', '')}, "
            f"ngày thi {bai_thi.get('ngay_thi', '')}.\n"
        )

        reply += "\nChi tiết các mã bài thi:\n"
        for item in cac_ma:
            reply += f"- {item.get('ma', '')}: "
            reply += f"tự luận {item.get('tu_luan_bat_buoc', '')}; "
            reply += f"trắc nghiệm bắt buộc gồm {', '.join(item.get('trac_nghiem_bat_buoc', []))}; "
            reply += f"môn tự chọn là {item.get('trac_nghiem_tu_chon', '')}.\n"

    elif "ngành" in q or "tổ hợp" in q or "mã ngành" in q:
        nganh_list = ts.get("nganh_tuyen_sinh", [])
        reply = "Thông tin ngành tuyển sinh như sau:\n"
        for nganh in nganh_list:
            reply += f"- Tên ngành: {nganh.get('ten_nganh', '')}\n"
            reply += f"  Mã ngành: {nganh.get('ma_nganh', '')}\n"
            reply += f"  Mã trường: {nganh.get('ma_truong', '')}\n"
            reply += f"  Địa bàn tuyển sinh: {nganh.get('dia_ban', '')}\n"
            reply += f"  Tổ hợp xét tuyển: {', '.join(nganh.get('to_hop_xet_tuyen_pt3', []))}\n"
            reply += f"  Mã bài thi đánh giá: {', '.join(nganh.get('ma_bai_thi_danh_gia', []))}\n"

    elif "mã trường" in q or "css" in q or "trường" in q:
        tt = data.get("thong_tin_chung", {})
        dia_chi = tt.get("dia_chi", {})
        lien_he = tt.get("lien_he_tuyen_sinh", [])

        reply = (
            f"Thông tin chung của trường:\n"
            f"- Tên trường: {tt.get('ten_truong_vi', '')}\n"
            f"- Tên tiếng Anh: {tt.get('ten_truong_en', '')}\n"
            f"- Mã trường: {tt.get('ma_truong', '')}\n"
            f"- Website: {tt.get('website', '')}\n"
            f"- Trụ sở chính: {dia_chi.get('tru_so_chinh', '')}\n"
            f"- Cơ sở 2: {dia_chi.get('co_so_2', '')}\n"
            f"- Cơ sở 3: {dia_chi.get('co_so_3', '')}\n"
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


def build_context(query: str) -> Optional[str]:
    q = query.lower().strip()

    builders = [
        build_schedule_context,
        build_document_context,
        build_study_material_context,
        build_library_context,
        build_admission_context,
    ]

    context_parts = []
    for builder in builders:
        result = builder(q)
        if result:
            context_parts.append(result)

    if not context_parts:
        return None

    return "\n\n".join(context_parts)


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
