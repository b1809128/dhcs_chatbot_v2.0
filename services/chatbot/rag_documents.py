from functools import lru_cache
from typing import Iterable, List, TypedDict

from .types import JsonDict, StructuredContext
from .utils import load_data


class RagDocument(TypedDict):
    id: str
    title: str
    text: str
    domain: str
    source_file: str
    keywords: List[str]
    file_url: str
    download_url: str
    file_type: str

def _stringify(value: object) -> str:
    if isinstance(value, list):
        return "; ".join(_stringify(item) for item in value if item)
    if isinstance(value, dict):
        return "; ".join(f"{key}: {_stringify(item)}" for key, item in value.items() if item)
    return str(value or "").strip()


def _build_document(
    *,
    doc_id: str,
    title: str,
    text: str,
    domain: str,
    source_file: str,
    keywords: Iterable[str] = (),
    file_url: str = "",
    download_url: str = "",
    file_type: str = "",
) -> RagDocument | None:
    clean_text = text.strip()
    if not clean_text:
        return None

    return {
        "id": doc_id,
        "title": title.strip(),
        "text": clean_text,
        "domain": domain,
        "source_file": source_file,
        "keywords": [str(item).strip() for item in keywords if str(item).strip()],
        "file_url": file_url,
        "download_url": download_url,
        "file_type": file_type,
    }


def _document_file_metadata(file_path: str) -> JsonDict:
    if not file_path:
        return {"file_url": "", "download_url": "", "file_type": ""}

    file_type = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else "file"
    return {
        "file_url": f"/documents/{file_path}",
        "download_url": f"/documents/download/{file_path}",
        "file_type": file_type,
    }


def _chunk_tuyen_sinh() -> List[RagDocument]:
    data = load_data("tuyen_sinh.json")
    if not data:
        return []

    docs: List[RagDocument] = []
    thong_tin = data.get("thong_tin_chung", {})
    ts = data.get("tuyen_sinh_dai_hoc_chinh_quy", {})
    bai_thi = data.get("bai_thi_danh_gia_bo_cong_an", {})
    source_file = "tuyen_sinh.json"
    source_metadata = _document_file_metadata(data.get("nguon", {}).get("file_pdf", ""))

    common_info = _build_document(
        doc_id="tuyen-sinh-thong-tin-chung",
        title="Thông tin chung tuyển sinh",
        text=(
            f"Tên trường: {thong_tin.get('ten_truong_vi', '')}. "
            f"Tên tiếng Anh: {thong_tin.get('ten_truong_en', '')}. "
            f"Mã trường: {thong_tin.get('ma_truong', '')}. "
            f"Website: {thong_tin.get('website', '')}. "
            f"Email tuyển sinh: {thong_tin.get('email_tuyen_sinh', '')}. "
            f"Trụ sở chính: {thong_tin.get('dia_chi', {}).get('tru_so_chinh', '')}. "
            f"Cơ sở 2: {thong_tin.get('dia_chi', {}).get('co_so_2', '')}. "
            f"Cơ sở 3: {thong_tin.get('dia_chi', {}).get('co_so_3', '')}. "
            f"Việc làm sau tốt nghiệp: {thong_tin.get('viec_lam_sau_tot_nghiep', '')}. "
            f"Liên hệ tuyển sinh: {_stringify(thong_tin.get('lien_he_tuyen_sinh', []))}."
        ),
        domain="tuyen_sinh",
        source_file=source_file,
        keywords=data.get("tu_khoa_goi_y", []),
        **source_metadata,
    )
    if common_info:
        docs.append(common_info)

    sections = [
        (
            "thong-bao",
            "Thông báo tuyển sinh VB2CA 2026",
            data.get("thong_bao_tuyen_sinh", {}),
            ["thông báo 56", "56/TB-CAT-PX01", "VB2CA", "tuyển sinh 2026"],
        ),
        (
            "doi-tuong-du-tuyen",
            "Đối tượng dự tuyển",
            ts.get("doi_tuong_du_tuyen", []),
            ["đối tượng dự tuyển", "văn bằng 2", "vb2", "chiến sĩ nghĩa vụ"],
        ),
        (
            "dieu-kien-chung",
            "Điều kiện chung",
            ts.get("dieu_kien_chung", []),
            ["điều kiện", "điều kiện dự tuyển", "lý lịch", "sức khỏe", "văn bằng 2"],
        ),
        (
            "tieu-chuan-suc-khoe",
            "Tiêu chuẩn sức khỏe tuyển sinh",
            ts.get("tieu_chuan_suc_khoe", []),
            ["sức khỏe", "chiều cao", "BMI", "thị lực", "Thông tư 62", "Thông tư 131"],
        ),
        (
            "pham-vi",
            "Phạm vi tuyển sinh",
            ts.get("pham_vi_tuyen_sinh", {}),
            ["phạm vi", "địa bàn", "phía Nam", "toàn quốc", "CSS", "T05"],
        ),
        (
            "phuong-thuc",
            "Phương thức tuyển sinh",
            ts.get("phuong_thuc_tuyen_sinh", []),
            ["phương thức", "xét tuyển", "thi tuyển", "vb2ca"],
        ),
        (
            "chi-tieu",
            "Chỉ tiêu tuyển sinh",
            {
                "tong_hop": ts.get("chi_tieu", {}),
                "theo_truong": ts.get("chi_tieu_theo_truong", []),
            },
            ["chỉ tiêu", "nam", "nữ", "số lượng tuyển"],
        ),
        (
            "nganh",
            "Ngành tuyển sinh",
            {
                "nganh_tuyen_sinh": ts.get("nganh_tuyen_sinh", []),
                "nganh_duoc_phep_dang_ky": ts.get("nganh_duoc_phep_dang_ky", []),
            },
            ["ngành", "ngành được phép đăng ký", "mã ngành", "mã trường", "css"],
        ),
        (
            "ho-so-so-tuyen",
            "Hồ sơ sơ tuyển",
            ts.get("ho_so_nhap_hoc", []),
            ["hồ sơ", "hồ sơ sơ tuyển", "giấy tờ", "đăng ký dự tuyển"],
        ),
        (
            "thu-tuc-dang-ky",
            "Thủ tục đăng ký sơ tuyển",
            ts.get("thu_tuc_dang_ky", {}),
            ["sơ tuyển", "đăng ký sơ tuyển", "hạn đăng ký", "lệ phí sơ tuyển"],
        ),
        (
            "xet-tuyen-tinh-diem",
            "Xét tuyển và cách tính điểm",
            ts.get("xet_tuyen_va_tinh_diem", {}),
            ["xét tuyển", "cách tính điểm", "ĐXT", "BTBCA", "điểm cộng"],
        ),
        (
            "uu-tien",
            "Ưu tiên tuyển sinh",
            ts.get("uu_tien_trong_tuyen_sinh", []),
            ["ưu tiên", "điểm thưởng", "IELTS", "con cán bộ Công an"],
        ),
        (
            "dao-tao-chinh-sach",
            "Đào tạo và chính sách sau trúng tuyển",
            {
                "thoi_gian_dia_diem_dao_tao": ts.get("thoi_gian_dia_diem_dao_tao", {}),
                "che_do_chinh_sach": ts.get("che_do_chinh_sach", []),
            },
            ["đào tạo", "chính sách", "phong hàm", "Trung úy", "phân công công tác"],
        ),
        (
            "bai-thi",
            "Bài thi đánh giá Bộ Công an",
            bai_thi,
            ["bài thi", "vb2ca", "ca1", "ca2", "ca3", "ca4", "ngưỡng đầu vào"],
        ),
    ]

    for suffix, title, value, keywords in sections:
        document = _build_document(
            doc_id=f"tuyen-sinh-{suffix}",
            title=title,
            text=_stringify(value),
            domain="tuyen_sinh",
            source_file=source_file,
            keywords=[title, *keywords, *data.get("tu_khoa_goi_y", [])],
            **source_metadata,
        )
        if document:
            docs.append(document)

    return docs


def _chunk_thu_vien() -> List[RagDocument]:
    data = load_data("thu_vien.json")
    if not data:
        return []

    docs: List[RagDocument] = []
    source_file = "thu_vien.json"

    sections = [
        ("thong-tin", "Thông tin thư viện", data.get("thong_tin_thu_vien", {})),
        ("quy-dinh", "Quy định mượn trả", data.get("quy_dinh_muon_tra", {})),
        ("ke-sach", "Danh mục kệ thư viện", data.get("danh_muc_ke", [])),
    ]

    for suffix, title, value in sections:
        document = _build_document(
            doc_id=f"thu-vien-{suffix}",
            title=title,
            text=_stringify(value),
            domain="thu_vien",
            source_file=source_file,
            keywords=["thư viện", "mượn sách", "giờ mở cửa", "liên hệ thư viện"],
        )
        if document:
            docs.append(document)

    for index, book in enumerate(data.get("thu_vien", []), start=1):
        document = _build_document(
            doc_id=f"thu-vien-book-{index}",
            title=book.get("ten_sach", f"Tài liệu thư viện {index}"),
            text=(
                f"Tên sách: {book.get('ten_sach', '')}. "
                f"Mã tài liệu: {book.get('ma_tai_lieu', '')}. "
                f"Tác giả: {book.get('tac_gia', '')}. "
                f"Lĩnh vực: {book.get('linh_vuc', '')}. "
                f"Vị trí kệ: {book.get('ke_sach', '')}. "
                f"Vị trí chi tiết: {book.get('vi_tri_chi_tiet', '')}. "
                f"Tình trạng: {book.get('tinh_trang', '')}. "
                f"Số lượng còn: {book.get('so_luong', '')}. "
                f"Thời gian mượn: {book.get('thoi_gian_muon', '')}. "
                f"Hình thức khai thác: {book.get('hinh_thuc_khai_thac', '')}. "
                f"Ghi chú: {book.get('ghi_chu', '')}."
            ),
            domain="thu_vien",
            source_file=source_file,
            keywords=book.get("tu_khoa", []),
        )
        if document:
            docs.append(document)

    return docs


def _chunk_ho_so() -> List[RagDocument]:
    data = load_data("ho_so.json")
    if not data:
        return []

    docs: List[RagDocument] = []
    source_file = "ho_so.json"

    for section_name, items in data.items():
        if not isinstance(items, list):
            continue
        for index, item in enumerate(items, start=1):
            title = item.get("ten", f"{section_name} {index}")
            file_path = item.get("file_pdf", "") or item.get("file_word", "")
            file_metadata = _document_file_metadata(file_path)
            document = _build_document(
                doc_id=f"ho-so-{section_name}-{index}",
                title=title,
                text=(
                    f"Loại: {section_name}. "
                    f"Tên: {item.get('ten', '')}. "
                    f"Số hiệu: {item.get('so_hieu', '')}. "
                    f"Ngày ban hành: {item.get('ngay_ban_hanh', '')}. "
                    f"Ngày hiệu lực: {item.get('ngay_hieu_luc', '')}. "
                    f"Trạng thái: {item.get('trang_thai', '')}. "
                    f"Nội dung: {item.get('noi_dung', '')}. "
                    f"Tóm tắt: {item.get('tom_tat', '')}. "
                    f"Cơ quan ban hành: {item.get('co_quan_ban_hanh', '')}. "
                    f"Mô tả: {item.get('mo_ta', '')}. "
                    f"Nội dung mẫu: {item.get('noi_dung_mau', '')}. "
                    f"File PDF: {item.get('file_pdf', '')}. "
                    f"File Word: {item.get('file_word', '')}."
                ),
                domain="ho_so",
                source_file=source_file,
                keywords=item.get("tu_khoa", []),
                **file_metadata,
            )
            if document:
                docs.append(document)

    return docs


def _chunk_pdf_word_metadata() -> List[RagDocument]:
    documents = []
    exam_files = {
        "CA1": "de_thi/CA1.pdf",
        "CA2": "de_thi/CA2.pdf",
        "CA3": "de_thi/CA3.pdf",
        "CA4": "de_thi/CA4.pdf",
    }

    for exam_code, file_path in exam_files.items():
        document = _build_document(
            doc_id=f"de-thi-vb2ca-{exam_code.lower()}",
            title=f"Đề thi VB2CA {exam_code}",
            text=(
                f"Đề thi tham khảo mã {exam_code} thuộc kỳ bài thi đánh giá VB2CA. "
                "Có thể xem nhanh file PDF hoặc tải về để ôn tập."
            ),
            domain="de_thi",
            source_file=file_path,
            keywords=["bài thi", "vb2ca", exam_code.lower(), exam_code, "đề thi"],
            **_document_file_metadata(file_path),
        )
        if document:
            documents.append(document)

    word_file_path = "word_don_xin_nghi/nghi_phep.docx"
    word_document = _build_document(
        doc_id="word-don-xin-nghi-phep",
        title="Đơn xin nghỉ phép",
        text=(
            "Biểu mẫu Word đơn xin nghỉ phép dùng khi học viên xin nghỉ học, "
            "xin ra ngoài hoặc cần tải mẫu đơn để chỉnh sửa."
        ),
        domain="bieu_mau",
        source_file=word_file_path,
        keywords=["đơn xin phép", "đơn xin nghỉ phép", "word", "biểu mẫu", "nghi_phep"],
        **_document_file_metadata(word_file_path),
    )
    if word_document:
        documents.append(word_document)

    return documents


def _chunk_tai_lieu() -> List[RagDocument]:
    data = load_data("tai_lieu.json")
    if not data:
        return []

    docs: List[RagDocument] = []
    source_file = "tai_lieu.json"

    overview = _build_document(
        doc_id="tai-lieu-overview",
        title="Hỗ trợ học tập",
        text=(
            f"Mô tả: {data.get('mo_ta', '')}. "
            f"Lĩnh vực: {_stringify(data.get('linh_vuc', []))}. "
            f"Ví dụ câu hỏi: {_stringify(data.get('vi_du_cau_hoi', []))}. "
            f"Định dạng trả lời: {_stringify(data.get('dinh_dang_tra_loi', []))}."
        ),
        domain="tai_lieu",
        source_file=source_file,
        keywords=data.get("linh_vuc", []),
    )
    if overview:
        docs.append(overview)

    for index, item in enumerate(data.get("chuc_nang", []), start=1):
        document = _build_document(
            doc_id=f"tai-lieu-{index}",
            title=item.get("ten", f"Chức năng hỗ trợ {index}"),
            text=_stringify(item.get("noi_dung", [])),
            domain="tai_lieu",
            source_file=source_file,
            keywords=[item.get("ten", ""), *data.get("linh_vuc", [])],
        )
        if document:
            docs.append(document)

    return docs


def _chunk_lich_hoc() -> List[RagDocument]:
    data = load_data("lich_hoc.json")
    if not data:
        return []

    docs: List[RagDocument] = []
    source_file = "lich_hoc.json"

    for section_name, items in data.items():
        if not isinstance(items, list):
            continue
        for index, item in enumerate(items, start=1):
            document = _build_document(
                doc_id=f"lich-hoc-{section_name}-{index}",
                title=f"{section_name.replace('_', ' ').title()} {index}",
                text=_stringify(item),
                domain="lich_hoc",
                source_file=source_file,
                keywords=[section_name, item.get("lop", ""), item.get("mon", "")],
            )
            if document:
                docs.append(document)

    return docs


@lru_cache(maxsize=1)
def build_rag_documents() -> tuple[RagDocument, ...]:
    documents: List[RagDocument] = []
    documents.extend(_chunk_tuyen_sinh())
    documents.extend(_chunk_thu_vien())
    documents.extend(_chunk_ho_so())
    documents.extend(_chunk_pdf_word_metadata())
    documents.extend(_chunk_tai_lieu())
    documents.extend(_chunk_lich_hoc())
    return tuple(documents)



def build_structured_seed_document(data: StructuredContext) -> RagDocument | None:
    title = data.get("title", "").strip() or "Thông tin nội bộ"
    text = data.get("message", "").strip()
    if not text:
        return None

    return {
        "id": "structured-seed",
        "title": title,
        "text": text,
        "domain": "structured",
        "source_file": "structured_context",
        "keywords": [title],
        "file_url": "",
        "download_url": "",
        "file_type": "",
    }
