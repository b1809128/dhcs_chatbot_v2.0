from typing import List, Optional

from .types import StructuredContext
from .utils import contains_any


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

    if title in {"CÔNG VĂN", "THÔNG TƯ", "NGHỊ ĐỊNH", "LUẬT", "BIỂU MẪU / ĐƠN", "TỔ CHỨC"}:
        if "đơn" in normalized_query:
            return [
                "Đơn nghỉ tranh thủ",
                "Công văn",
                "Thông tư",
                "Đoàn thanh niên",
            ]
        if contains_any(normalized_query, ["luật an ninh mạng", "luat an ninh mang", "luat_an_ninh_mang"]):
            return [
                "Thông tư 62_2023",
                "Nghị định",
                "Công văn",
                "Đơn xin phép",
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

    if title in {
        "TUYỂN SINH",
        "BÀI THI ĐÁNH GIÁ",
        "HỒ SƠ TUYỂN SINH",
        "NGÀNH TUYỂN SINH",
        "THÔNG TIN TRƯỜNG",
        "LIÊN HỆ TUYỂN SINH",
    }:
        if "chỉ tiêu" in normalized_query:
            return [
                "Phương thức tuyển sinh",
                "Điều kiện dự tuyển",
                "Hồ sơ nhập học",
                "Ngành tuyển sinh",
                "Bài thi VB2CA",
                "Ngưỡng đầu vào",
                "Chứng chỉ IELTS",
                "Mã trường CSS",
            ]
        if contains_any(normalized_query, ["vb2ca", "bài thi", "ca1", "ca2", "ca3", "ca4"]):
            return [
                "Ngưỡng đầu vào",
                "Chứng chỉ IELTS",
                "Hồ sơ nhập học",
                "Mã trường CSS",
                "Chỉ tiêu tuyển sinh",
                "Phương thức tuyển sinh",
                "Ngành tuyển sinh",
                "Liên hệ tuyển sinh",
            ]
        if contains_any(normalized_query, ["hồ sơ", "nhập học"]):
            return [
                "Điều kiện dự tuyển",
                "Chỉ tiêu tuyển sinh",
                "Phương thức tuyển sinh",
                "Ngành tuyển sinh",
                "Bài thi VB2CA",
                "Chứng chỉ IELTS",
                "Mã trường CSS",
                "Liên hệ tuyển sinh",
            ]
        if contains_any(normalized_query, ["mã trường", "css", "liên hệ", "email"]):
            return [
                "Chỉ tiêu tuyển sinh",
                "Phương thức tuyển sinh",
                "Điều kiện dự tuyển",
                "Hồ sơ nhập học",
                "Ngành tuyển sinh",
                "Bài thi VB2CA",
                "Ngưỡng đầu vào",
                "Chứng chỉ IELTS",
            ]
        return [
            "Chỉ tiêu tuyển sinh",
            "Phương thức tuyển sinh",
            "Điều kiện dự tuyển",
            "Hồ sơ nhập học",
            "Ngành tuyển sinh",
            "Bài thi VB2CA",
            "Chứng chỉ IELTS",
            "Mã trường CSS",
            "Ngưỡng đầu vào",
            "Liên hệ tuyển sinh",
        ]

    if title == "TÀI LIỆU NGHIỆP VỤ":
        return [
            "Giải thích bài giảng",
            "Tóm tắt giáo trình",
            "Tạo câu hỏi ôn tập",
            "Gợi ý phương pháp học",
        ]

    return []
