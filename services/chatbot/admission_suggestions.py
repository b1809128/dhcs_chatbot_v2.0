from typing import List

from .utils import contains_any


ADMISSION_OVERVIEW_SUGGESTIONS = [
    "Thông báo 56/TB-CAT-PX01",
    "Đối tượng dự tuyển VB2CA",
    "Điều kiện trình độ đào tạo",
    "Không quá 30 tuổi",
    "Tiêu chuẩn chính trị",
    "Tiêu chuẩn sức khỏe",
    "Chiều cao dự tuyển",
    "BMI tuyển sinh",
    "Thị lực dự tuyển",
    "Chỉ tiêu theo từng trường",
    "Chỉ tiêu Trường Đại học Cảnh sát nhân dân",
    "Mã ngành 7860100",
    "Mã trường CSS",
    "Ngành được phép đăng ký",
    "Phạm vi tuyển sinh phía Nam",
    "Phương thức 1 xét tuyển thẳng",
    "Phương thức 2 thi tuyển",
    "Ngày thi 20/09/2026",
    "Thi trên máy tính",
    "Ngưỡng đầu vào",
    "Cách tính điểm xét tuyển",
    "Ưu tiên tuyển sinh",
    "Điểm thưởng IELTS",
    "Thủ tục đăng ký sơ tuyển",
    "Hồ sơ sơ tuyển",
    "Lệ phí sơ tuyển",
    "Hạn đăng ký 25/06/2026",
    "Thời gian đào tạo",
    "Chính sách sau tốt nghiệp",
    "Liên hệ tuyển sinh ĐHCS",
]

ADMISSION_BY_TOPIC = {
    "van_bang_2": [
        "Đối tượng dự tuyển VB2CA",
        "Điều kiện trình độ đào tạo",
        "Chỉ tiêu Trường Đại học Cảnh sát nhân dân",
        "Phương thức 1 xét tuyển thẳng",
        "Phương thức 2 thi tuyển",
        "Ngày thi 20/09/2026",
        "Ngưỡng đầu vào",
        "Ngành được phép đăng ký",
        "Hồ sơ sơ tuyển",
        "Lệ phí sơ tuyển",
        "Tiêu chuẩn sức khỏe",
        "Liên hệ tuyển sinh ĐHCS",
    ],
    "chi_tieu": [
        "Chỉ tiêu theo từng trường",
        "Chỉ tiêu Trường Đại học Cảnh sát nhân dân",
        "Chỉ tiêu phương thức 1",
        "Chỉ tiêu phương thức 2",
        "Mã trường CSS",
        "Mã ngành 7860100",
        "Phạm vi tuyển sinh phía Nam",
        "Phương thức 1 xét tuyển thẳng",
        "Phương thức 2 thi tuyển",
        "Ngưỡng đầu vào",
        "Hồ sơ sơ tuyển",
        "Liên hệ tuyển sinh",
    ],
    "vb2ca": [
        "Ngày thi 20/09/2026",
        "Thi trên máy tính",
        "Ngưỡng đầu vào",
        "Cách tính điểm xét tuyển",
        "Xem đề thi CA1",
        "Xem đề thi CA2",
        "Xem đề thi CA3",
        "Xem đề thi CA4",
        "Địa điểm thi VB2CA",
        "Phương thức 2 thi tuyển",
        "Điểm thưởng IELTS",
        "Hồ sơ sơ tuyển",
    ],
    "ho_so": [
        "Hồ sơ sơ tuyển gồm những gì",
        "Đơn đăng ký dự tuyển",
        "Căn cước công dân",
        "Bằng tốt nghiệp và bảng điểm",
        "Chứng chỉ ngoại ngữ nếu có",
        "Văn bằng nước ngoài cần gì",
        "Thủ tục đăng ký sơ tuyển",
        "Lệ phí sơ tuyển",
        "Hạn đăng ký 25/06/2026",
        "Điều kiện trình độ đào tạo",
        "Liên hệ tuyển sinh",
        "Mã trường CSS",
        "Ngành được phép đăng ký",
    ],
    "lien_he": [
        "Email tuyển sinh",
        "Website tuyển sinh",
        "Số điện thoại tuyển sinh",
        "Địa chỉ trụ sở chính",
        "Mã trường CSS",
        "Liên hệ tuyển sinh ĐHCS",
        "Phạm vi tuyển sinh phía Nam",
        "Thủ tục đăng ký sơ tuyển",
        "Hạn đăng ký 25/06/2026",
        "Chỉ tiêu Trường Đại học Cảnh sát nhân dân",
        "Hồ sơ sơ tuyển",
    ],
    "dieu_kien": [
        "Đối tượng dự tuyển VB2CA",
        "Điều kiện trình độ đào tạo",
        "Điều kiện xếp loại bằng đại học",
        "Không quá 30 tuổi",
        "Tiêu chuẩn chính trị",
        "Tiêu chuẩn sức khỏe",
        "Chiều cao dự tuyển",
        "BMI tuyển sinh",
        "Thị lực dự tuyển",
        "Điều kiện chiến sĩ nghĩa vụ Công an",
        "Ngành được phép đăng ký",
        "Hồ sơ sơ tuyển",
    ],
    "nganh": [
        "Ngành được phép đăng ký",
        "Mã ngành 7860100",
        "Mã trường CSS",
        "Ngành nghiệp vụ Cảnh sát",
        "Ngành An toàn thông tin",
        "Ngành Phòng cháy chữa cháy",
        "Nhóm ngành Kỹ thuật - Hậu cần",
        "Phạm vi tuyển sinh phía Nam",
        "Chỉ tiêu theo từng trường",
        "Điều kiện trình độ đào tạo",
        "Ngưỡng đầu vào",
        "Liên hệ tuyển sinh",
    ],
    "chung_chi": [
        "Ưu tiên tuyển sinh",
        "Điểm thưởng IELTS 6.5",
        "Điểm thưởng IELTS 6.0",
        "Hạn chứng chỉ ngoại ngữ",
        "Con cán bộ Công an được cộng điểm không",
        "Phương thức 1 xét tuyển thẳng",
        "Cách tính điểm xét tuyển",
        "Ngưỡng đầu vào",
        "Hồ sơ sơ tuyển",
        "Liên hệ tuyển sinh",
    ],
    "so_tuyen": [
        "Thủ tục đăng ký sơ tuyển",
        "Hồ sơ sơ tuyển gồm những gì",
        "Lệ phí sơ tuyển",
        "Hạn đăng ký 25/06/2026",
        "Nơi đăng ký sơ tuyển",
        "Đối tượng dự tuyển VB2CA",
        "Tiêu chuẩn sức khỏe",
        "Liên hệ tuyển sinh ĐHCS",
        "Mã trường CSS",
        "Chỉ tiêu Trường Đại học Cảnh sát nhân dân",
    ],
    "dao_tao": [
        "Thời gian đào tạo",
        "Địa điểm đào tạo",
        "Chính sách sau tốt nghiệp",
        "Phong hàm Trung úy",
        "Phân công công tác sau tốt nghiệp",
        "Chỉ tiêu Trường Đại học Cảnh sát nhân dân",
        "Liên hệ tuyển sinh ĐHCS",
    ],
    "precheck": [
        "Kiểm tra sơ bộ điều kiện với tuổi, chiều cao, BMI",
        "Điều kiện xếp loại bằng đại học",
        "Điều kiện ngành CNTT đăng ký CSS",
        "Tiêu chuẩn sức khỏe",
        "Ngành được phép đăng ký",
        "Checklist hồ sơ sơ tuyển",
        "So sánh phương thức tuyển sinh",
        "Liên hệ tuyển sinh ĐHCS",
    ],
    "conflict": [
        "Điều kiện trình độ đào tạo",
        "Đối tượng dự tuyển VB2CA",
        "Ngành được phép đăng ký",
        "Kiểm tra sơ bộ điều kiện",
        "Checklist hồ sơ sơ tuyển",
        "Liên hệ tuyển sinh ĐHCS",
    ],
    "summary_view": [
        "Timeline tuyển sinh VB2CA 2026",
        "Checklist hồ sơ sơ tuyển",
        "So sánh phương thức tuyển sinh",
        "Chỉ tiêu CSS",
        "Ngày thi 20/09/2026",
        "Tài liệu và hành động tuyển sinh",
        "Kiểm tra sơ bộ điều kiện",
    ],
    "timeline_view": [
        "Hạn đăng ký 25/06/2026",
        "Ngày thi 20/09/2026",
        "Checklist hồ sơ sơ tuyển",
        "Lệ phí sơ tuyển",
        "Tài liệu và hành động tuyển sinh",
        "Liên hệ tuyển sinh ĐHCS",
    ],
    "checklist_view": [
        "Thủ tục đăng ký sơ tuyển",
        "Lệ phí sơ tuyển",
        "Hạn đăng ký 25/06/2026",
        "Bằng tốt nghiệp và bảng điểm",
        "Văn bằng nước ngoài cần gì",
        "Liên hệ tuyển sinh ĐHCS",
        "Kiểm tra sơ bộ điều kiện",
    ],
    "method_compare": [
        "Phương thức 1 xét tuyển thẳng",
        "Phương thức 2 thi tuyển",
        "Điểm thưởng IELTS",
        "Cách tính điểm xét tuyển",
        "Ngưỡng đầu vào",
        "Ngày thi 20/09/2026",
        "Chỉ tiêu theo từng trường",
    ],
    "action_documents": [
        "Tải thông báo tuyển sinh",
        "Xem đề thi CA1",
        "Xem đề thi CA2",
        "Xem đề thi CA3",
        "Xem đề thi CA4",
        "Timeline tuyển sinh VB2CA 2026",
        "Checklist hồ sơ sơ tuyển",
    ],
    "professional": [
        "Tóm tắt tuyển sinh VB2CA 2026",
        "Timeline tuyển sinh VB2CA 2026",
        "Checklist hồ sơ sơ tuyển",
        "So sánh phương thức tuyển sinh",
        "Kiểm tra sơ bộ điều kiện",
        "Tài liệu và hành động tuyển sinh",
    ],
}

ADMISSION_ACTIONABLE_SUGGESTIONS = [
    "Tóm tắt tuyển sinh VB2CA 2026",
    "Kiểm tra sơ bộ điều kiện",
    "Timeline tuyển sinh VB2CA 2026",
    "Checklist hồ sơ sơ tuyển",
    "So sánh phương thức tuyển sinh",
    "Tài liệu và hành động tuyển sinh",
]

ADMISSION_TITLE_TOPIC_MAP = {
    "TUYỂN SINH VĂN BẰNG 2": "van_bang_2",
    "BÀI THI ĐÁNH GIÁ": "vb2ca",
    "THÔNG TIN BÀI THI ĐÁNH GIÁ": "vb2ca",
    "HỒ SƠ TUYỂN SINH": "ho_so",
    "THỦ TỤC SƠ TUYỂN": "so_tuyen",
    "CHỈ TIÊU TUYỂN SINH": "chi_tieu",
    "LIÊN HỆ TUYỂN SINH": "lien_he",
    "THÔNG TIN TRƯỜNG": "lien_he",
    "TIÊU CHUẨN SỨC KHỎE": "dieu_kien",
    "NGÀNH TUYỂN SINH": "nganh",
    "NGÀNH ĐƯỢC PHÉP ĐĂNG KÝ": "nganh",
    "ƯU TIÊN TUYỂN SINH": "chung_chi",
    "XÉT TUYỂN VÀ CÁCH TÍNH ĐIỂM": "chung_chi",
    "ĐÀO TẠO VÀ CHÍNH SÁCH": "dao_tao",
    "KIỂM TRA SƠ BỘ ĐIỀU KIỆN": "precheck",
    "TÓM TẮT TUYỂN SINH VB2CA 2026": "summary_view",
    "TIMELINE TUYỂN SINH VB2CA 2026": "timeline_view",
    "CHECKLIST HỒ SƠ SƠ TUYỂN": "checklist_view",
    "SO SÁNH PHƯƠNG THỨC TUYỂN SINH": "method_compare",
    "TÀI LIỆU VÀ HÀNH ĐỘNG TUYỂN SINH": "action_documents",
    "LƯU Ý MÂU THUẪN": "conflict",
}

ADMISSION_TITLES = {
    "TUYỂN SINH",
    "PHẠM VI TUYỂN SINH",
    "THÔNG BÁO TUYỂN SINH",
    *ADMISSION_TITLE_TOPIC_MAP.keys(),
}

TOPICS_WITHOUT_EXTRA_ACTIONS = {
    "summary_view",
    "timeline_view",
    "checklist_view",
    "method_compare",
    "action_documents",
    "professional",
}


def merge_suggestions(*groups: List[str]) -> List[str]:
    suggestions = []
    seen = set()

    for group in groups:
        for item in group:
            normalized_item = item.lower().strip()
            if normalized_item and normalized_item not in seen:
                suggestions.append(item)
                seen.add(normalized_item)

    return suggestions


def merge_admission_topic(
    topic: str,
    *,
    include_overview: bool = True,
    include_actions: bool = True,
) -> List[str]:
    groups = [ADMISSION_BY_TOPIC[topic]]
    if include_actions:
        groups.append(ADMISSION_ACTIONABLE_SUGGESTIONS)
    if include_overview:
        groups.append(ADMISSION_OVERVIEW_SUGGESTIONS)
    return merge_suggestions(*groups)


def admission_suggestions_for_title(title: str) -> List[str]:
    topic = ADMISSION_TITLE_TOPIC_MAP.get(title)
    if not topic:
        return []

    return merge_admission_topic(topic, include_actions=topic not in TOPICS_WITHOUT_EXTRA_ACTIONS)


def get_admission_suggestions(normalized_query: str, title: str) -> List[str]:
    if title_suggestions := admission_suggestions_for_title(title):
        return title_suggestions

    if "chỉ tiêu" in normalized_query:
        return merge_admission_topic("chi_tieu")
    if contains_any(normalized_query, ["sơ tuyển", "lệ phí", "hạn đăng ký"]):
        return merge_admission_topic("so_tuyen")
    if contains_any(normalized_query, ["văn bằng 2", "van bang 2"]) or (
        "vb2" in normalized_query and "vb2ca" not in normalized_query
    ):
        return merge_admission_topic("van_bang_2")
    if contains_any(normalized_query, ["vb2ca", "bài thi", "ca1", "ca2", "ca3", "ca4"]):
        return merge_admission_topic("vb2ca")
    if contains_any(normalized_query, ["hồ sơ", "nhập học"]):
        return merge_admission_topic("ho_so")
    if contains_any(normalized_query, ["mã trường", "css", "liên hệ", "email"]):
        return merge_admission_topic("lien_he")
    if contains_any(normalized_query, ["điều kiện", "lý lịch", "sức khỏe", "đối tượng"]):
        return merge_admission_topic("dieu_kien")
    if contains_any(normalized_query, ["ngành", "mã ngành", "tổ hợp"]):
        return merge_admission_topic("nganh")
    if contains_any(normalized_query, ["chứng chỉ", "ielts", "ngoại ngữ", "điểm thưởng"]):
        return merge_admission_topic("chung_chi")
    if contains_any(normalized_query, ["đào tạo", "chính sách", "phong hàm", "phân công"]):
        return merge_admission_topic("dao_tao")

    return merge_suggestions(ADMISSION_ACTIONABLE_SUGGESTIONS, ADMISSION_OVERVIEW_SUGGESTIONS)
