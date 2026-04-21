import re

from .admission_helpers import extract_school_code, normalize_admission_query, with_source
from .types import StructuredContext
from .utils import build_table_context, contains_any


TECH_FIELD_KEYWORDS = [
    "cntt",
    "cong nghe thong tin",
    "công nghệ thông tin",
    "may tinh",
    "máy tính",
    "ky thuat",
    "kỹ thuật",
    "khoa hoc tu nhien",
    "khoa học tự nhiên",
]


def parse_height_cm(query: str) -> float | None:
    meter_match = re.search(r"(\d)\s*m\s*(\d{1,2})", query)
    if meter_match:
        return int(meter_match.group(1)) * 100 + int(meter_match.group(2))

    cm_match = re.search(r"(\d{2,3}(?:[.,]\d+)?)\s*cm", query)
    if cm_match:
        return float(cm_match.group(1).replace(",", "."))

    return None


def parse_admission_profile(query: str) -> dict:
    normalized = normalize_admission_query(query)
    age_match = re.search(r"(\d{2})\s*(?:tuổi|tuoi)", normalized)
    bmi_match = re.search(r"bmi\s*(\d{1,2}(?:[.,]\d+)?)", normalized)
    ielts_match = re.search(r"ielts(?:\s*academic)?\s*(\d(?:[.,]\d)?)", normalized)

    grade = ""
    for candidate in ["xuất sắc", "xuat sac", "giỏi", "gioi", "khá", "kha", "trung bình", "trung binh"]:
        if candidate in normalized:
            grade = candidate
            break

    return {
        "gender": "nam" if " nam" in f" {normalized} " else "nữ" if " nữ" in normalized or " nu" in normalized else "",
        "age": int(age_match.group(1)) if age_match else None,
        "height_cm": parse_height_cm(normalized),
        "bmi": float(bmi_match.group(1).replace(",", ".")) if bmi_match else None,
        "field": "kỹ thuật/CNTT" if contains_any(normalized, TECH_FIELD_KEYWORDS) else "",
        "grade": grade,
        "ielts": float(ielts_match.group(1).replace(",", ".")) if ielts_match else None,
        "soldier": contains_any(normalized, ["chiến sĩ nghĩa vụ", "chien si nghia vu", "công an tại ngũ", "cong an tai ngu"]),
        "school": extract_school_code(query) or "",
    }


def has_profile_signals(query: str) -> bool:
    normalized = normalize_admission_query(query)
    has_advice_intent = contains_any(
        normalized,
        [
            "có đăng ký",
            "co dang ky",
            "đủ điều kiện",
            "du dieu kien",
            "đăng ký được",
            "dang ky duoc",
            "xét giúp",
            "xet giup",
            "tư vấn",
            "tu van",
        ],
    )
    has_profile_detail = contains_any(
        normalized,
        ["cao ", "tuổi", "tuoi", "bmi", "tốt nghiệp", "tot nghiep", "cntt", "ielts"],
    )
    return has_advice_intent and has_profile_detail


def build_precheck_context(query: str, data: dict, ts: dict) -> StructuredContext:
    profile = parse_admission_profile(query)
    rows = []
    blockers = []
    missing = []

    def add(criterion: str, user_value: str, result: str, note: str) -> None:
        rows.append({"tieu_chi": criterion, "thong_tin": user_value or "Chưa cung cấp", "ket_qua": result, "ghi_chu": note})

    if profile["age"] is None:
        missing.append("tuổi")
        add("Tuổi", "", "Cần kiểm tra thêm", "Quy định: không quá 30 tuổi tính đến ngày dự thi.")
    elif profile["age"] <= 30:
        add("Tuổi", f"{profile['age']} tuổi", "Phù hợp sơ bộ", "Không quá 30 tuổi.")
    else:
        blockers.append("Tuổi vượt quá 30.")
        add("Tuổi", f"{profile['age']} tuổi", "Chưa phù hợp", "Quy định: không quá 30 tuổi tính đến ngày dự thi.")

    height = profile["height_cm"]
    gender = profile["gender"]
    if height is None:
        missing.append("chiều cao")
        add("Chiều cao", "", "Cần kiểm tra thêm", "Nam thường từ 1m64; nữ thường từ 1m58; có mức riêng cho một số đối tượng.")
    elif gender == "nam" and height < 164:
        blockers.append("Chiều cao nam dưới mức thông thường 1m64.")
        add("Chiều cao", f"Nam, {height:g} cm", "Chưa phù hợp", "Mức thông thường đối với nam: từ 1m64 đến 1m95.")
    elif gender == "nữ" and height < 158:
        blockers.append("Chiều cao nữ dưới mức thông thường 1m58.")
        add("Chiều cao", f"Nữ, {height:g} cm", "Chưa phù hợp", "Mức thông thường đối với nữ: từ 1m58 đến 1m80.")
    elif not gender:
        missing.append("giới tính")
        add("Chiều cao", f"{height:g} cm", "Cần kiểm tra thêm", "Cần biết giới tính/diện đối tượng để đối chiếu chính xác.")
    else:
        add("Chiều cao", f"{gender.capitalize()}, {height:g} cm", "Phù hợp sơ bộ", "Đạt mức chiều cao thông thường theo giới tính đã nêu.")

    if profile["bmi"] is None:
        missing.append("BMI")
        add("BMI", "", "Cần kiểm tra thêm", "Quy định: BMI từ 18.5 đến 30.")
    elif 18.5 <= profile["bmi"] <= 30:
        add("BMI", str(profile["bmi"]), "Phù hợp sơ bộ", "Nằm trong khoảng 18.5 đến 30.")
    else:
        blockers.append("BMI ngoài khoảng 18.5 đến 30.")
        add("BMI", str(profile["bmi"]), "Chưa phù hợp", "Quy định: BMI từ 18.5 đến 30.")

    grade = profile["grade"]
    if not grade:
        missing.append("xếp loại bằng")
        add("Xếp loại bằng đại học", "", "Cần kiểm tra thêm", "Thông thường yêu cầu tốt nghiệp đại học chính quy xếp loại khá trở lên; một số diện kỹ thuật/CNTT có điều kiện riêng.")
    elif grade in {"khá", "kha", "giỏi", "gioi", "xuất sắc", "xuat sac"}:
        add("Xếp loại bằng đại học", grade, "Phù hợp sơ bộ", "Đáp ứng mức khá trở lên theo điều kiện chung.")
    elif grade in {"trung bình", "trung binh"} and (profile["field"] or profile["soldier"]):
        add("Xếp loại bằng đại học", grade, "Cần kiểm tra thêm", "Có thể thuộc diện kỹ thuật/CNTT hoặc chiến sĩ nghĩa vụ, cần đối chiếu điều kiện chi tiết.")
    else:
        blockers.append("Xếp loại bằng chưa đạt điều kiện chung.")
        add("Xếp loại bằng đại học", grade, "Chưa phù hợp", "Điều kiện chung yêu cầu xếp loại khá trở lên.")

    if profile["field"]:
        add("Ngành đã tốt nghiệp", profile["field"], "Phù hợp sơ bộ", "CNTT/kỹ thuật là nhóm ngành có nhiều điều kiện phù hợp theo thông báo.")
    else:
        add("Ngành đã tốt nghiệp", "", "Cần kiểm tra thêm", "Cần biết ngành/chuyên ngành để đối chiếu ngành được phép đăng ký.")

    if profile["school"]:
        add("Trường muốn đăng ký", profile["school"], "Đã nhận diện", "Sẽ đối chiếu theo chỉ tiêu/mã trường trong thông báo.")
    else:
        add("Trường muốn đăng ký", "", "Cần kiểm tra thêm", "Có thể hỏi thêm theo mã ANH, ANS, CSS, PCH hoặc KTH.")

    if profile["ielts"] is not None:
        result = "Có thể được cộng/ưu tiên" if profile["ielts"] >= 6.0 else "Cần kiểm tra thêm"
        add("IELTS/chứng chỉ", f"IELTS {profile['ielts']}", result, "Điểm thưởng/điều kiện ưu tiên phụ thuộc mức điểm và phương thức xét tuyển.")
    else:
        add("IELTS/chứng chỉ", "", "Không bắt buộc cho mọi trường hợp", "Nếu có chứng chỉ phù hợp có thể liên quan phương thức 1 hoặc điểm thưởng.")

    if blockers:
        status = "Chưa phù hợp vì: " + "; ".join(blockers)
    elif missing:
        status = "Cần kiểm tra thêm: " + ", ".join(missing) + "."
    else:
        status = "Đủ điều kiện sơ bộ theo các thông tin đã cung cấp."

    rows.insert(0, {"tieu_chi": "Kết luận sơ bộ", "thong_tin": "", "ket_qua": status, "ghi_chu": "Kết quả chỉ để tham khảo, cần đối chiếu hồ sơ chính thức khi sơ tuyển."})
    return with_source(
        build_table_context("KIỂM TRA SƠ BỘ ĐIỀU KIỆN", ["Tiêu chí", "Thông tin", "Kết quả", "Ghi chú"], rows),
        data,
        "đối tượng, điều kiện chung, tiêu chuẩn sức khỏe, ngành được phép đăng ký",
    )
