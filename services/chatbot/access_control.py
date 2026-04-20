from .admission_context import build_admission_context
from .keywords import ADMISSION_KEYWORDS
from .utils import contains_any

PUBLIC_ADMISSION_SUGGESTIONS = [
    "Tuyển sinh văn bằng 2",
    "Chỉ tiêu tuyển sinh",
    "Phương thức tuyển sinh",
    "Điều kiện dự tuyển",
    "Hồ sơ nhập học",
    "Bài thi VB2CA",
    "Ngưỡng đầu vào",
    "Liên hệ tuyển sinh",
]

AUTHENTICATED_FEATURE_SUGGESTIONS = [
    "Lịch học",
    "Lịch thi",
    "Giờ mở cửa thư viện",
    "Thông tư",
    "Luật ban hành",
]


def is_public_query(question: str) -> bool:
    normalized_question = question.lower().strip()
    if not normalized_question:
        return False

    if build_admission_context(normalized_question) is not None:
        return True

    return contains_any(normalized_question, ADMISSION_KEYWORDS)


def get_initial_suggestions(is_authenticated: bool) -> list[str]:
    if is_authenticated:
        return AUTHENTICATED_FEATURE_SUGGESTIONS

    return PUBLIC_ADMISSION_SUGGESTIONS[:4]


def build_access_denied_response() -> dict:
    return {
        "reply": (
            "Bạn cần đăng nhập để sử dụng các chức năng nội bộ như lịch học, "
            "thư viện, tài liệu học tập hoặc biểu mẫu. Khi chưa đăng nhập, "
            "bạn chỉ có thể tra cứu thông tin tuyển sinh."
        ),
        "data": None,
        "suggestions": PUBLIC_ADMISSION_SUGGESTIONS,
    }
