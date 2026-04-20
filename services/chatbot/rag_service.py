import json
import math
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from typing import Iterable, List, TypedDict

from .config import INDEX_DIR
from .types import JsonDict, StructuredContext
from .utils import load_data


class RagDocument(TypedDict):
    id: str
    title: str
    text: str
    domain: str
    source_file: str
    keywords: List[str]


class RagIndex(TypedDict):
    documents: List[RagDocument]
    idf: JsonDict
    vectors: JsonDict


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")
STOP_WORDS = {
    "va",
    "và",
    "la",
    "là",
    "cua",
    "của",
    "cho",
    "ve",
    "về",
    "tai",
    "tại",
    "cac",
    "các",
    "nhung",
    "những",
    "mot",
    "một",
    "theo",
    "voi",
    "với",
    "trong",
    "khi",
    "neu",
    "nếu",
    "duoc",
    "được",
    "co",
    "có",
    "khong",
    "không",
    "tu",
    "từ",
    "den",
    "đến",
    "hoc",
    "học",
    "vien",
    "viên",
    "truong",
    "trường",
    "dai",
    "đại",
    "csnd",
    "dhcs",
}


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", str(text or "").lower())
    stripped = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", stripped).strip()


def tokenize(text: str) -> List[str]:
    tokens = TOKEN_PATTERN.findall(normalize_text(text))
    return [token for token in tokens if len(token) > 1 and token not in STOP_WORDS]


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
    )
    if common_info:
        docs.append(common_info)

    sections = [
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
            "phuong-thuc",
            "Phương thức tuyển sinh",
            ts.get("phuong_thuc_tuyen_sinh", []),
            ["phương thức", "xét tuyển", "thi tuyển", "vb2ca"],
        ),
        (
            "chi-tieu",
            "Chỉ tiêu tuyển sinh",
            ts.get("chi_tieu", {}),
            ["chỉ tiêu", "nam", "nữ", "số lượng tuyển"],
        ),
        (
            "nganh",
            "Ngành tuyển sinh",
            ts.get("nganh_tuyen_sinh", []),
            ["ngành", "mã ngành", "mã trường", "css"],
        ),
        (
            "ho-so",
            "Hồ sơ nhập học",
            ts.get("ho_so_nhap_hoc", []),
            ["hồ sơ", "nhập học", "giấy tờ", "giấy báo nhập học"],
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
                    f"Nội dung mẫu: {item.get('noi_dung_mau', '')}."
                ),
                domain="ho_so",
                source_file=source_file,
                keywords=item.get("tu_khoa", []),
            )
            if document:
                docs.append(document)

    return docs


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
    documents.extend(_chunk_tai_lieu())
    documents.extend(_chunk_lich_hoc())
    return tuple(documents)


def _document_tokens(document: RagDocument) -> List[str]:
    return tokenize(" ".join([document["title"], document["text"], *document["keywords"]]))


def _compute_sparse_tfidf(tokens: List[str], idf_map: dict[str, float]) -> dict[str, float]:
    if not tokens:
        return {}

    counts = Counter(tokens)
    total = sum(counts.values()) or 1
    weights = {
        token: (count / total) * idf_map[token]
        for token, count in counts.items()
        if token in idf_map
    }
    norm = math.sqrt(sum(weight * weight for weight in weights.values()))
    if norm == 0:
        return {}
    return {token: weight / norm for token, weight in weights.items()}


def _build_tfidf_index(documents: Iterable[RagDocument]) -> RagIndex:
    docs = list(documents)
    token_sets = [set(_document_tokens(document)) for document in docs]
    doc_count = len(token_sets) or 1

    df_counter: Counter[str] = Counter()
    for token_set in token_sets:
        df_counter.update(token_set)

    idf_map = {
        token: math.log((1 + doc_count) / (1 + frequency)) + 1.0
        for token, frequency in df_counter.items()
    }
    vectors = {
        document["id"]: _compute_sparse_tfidf(_document_tokens(document), idf_map)
        for document in docs
    }
    return {
        "documents": docs,
        "idf": idf_map,
        "vectors": vectors,
    }


def _index_file_path() -> str:
    return str(INDEX_DIR / "rag_index.json")


def _serialize_index(index: RagIndex) -> JsonDict:
    return {
        "documents": index["documents"],
        "idf": index["idf"],
        "vectors": index["vectors"],
    }


def _write_index(index: RagIndex) -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    path = INDEX_DIR / "rag_index.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(_serialize_index(index), file, ensure_ascii=False, indent=2)


def _load_index_from_disk() -> RagIndex | None:
    path = INDEX_DIR / "rag_index.json"
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    documents = payload.get("documents", [])
    idf = payload.get("idf", {})
    vectors = payload.get("vectors", {})
    if not documents or not idf or not vectors:
        return None

    return {
        "documents": documents,
        "idf": idf,
        "vectors": vectors,
    }


@lru_cache(maxsize=1)
def load_rag_index() -> RagIndex:
    disk_index = _load_index_from_disk()
    current_documents = list(build_rag_documents())

    if disk_index and len(disk_index["documents"]) == len(current_documents):
        return disk_index

    rebuilt_index = _build_tfidf_index(current_documents)
    _write_index(rebuilt_index)
    return rebuilt_index


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
    }


def _score_document(query: str, query_tokens: set[str], document: RagDocument) -> float:
    haystack = normalize_text(" ".join([document["title"], document["text"], *document["keywords"]]))
    if not haystack:
        return 0.0

    title_tokens = set(tokenize(document["title"]))
    doc_tokens = set(tokenize(haystack))
    if not doc_tokens:
        return 0.0

    overlap = query_tokens & doc_tokens
    title_overlap = query_tokens & title_tokens
    score = 0.0

    if overlap:
        score += len(overlap) * 3
        score += len(overlap) / math.sqrt(len(doc_tokens))

    if title_overlap:
        score += len(title_overlap) * 4

    normalized_query = normalize_text(query)
    if normalized_query and normalized_query in haystack:
        score += 8

    normalized_title = normalize_text(document["title"])
    if normalized_query and normalized_title and normalized_query in normalized_title:
        score += 10

    for keyword in document["keywords"]:
        normalized_keyword = normalize_text(keyword)
        if normalized_keyword and normalized_keyword in normalized_query:
            score += 4

    return score


def _cosine_similarity(query_vector: dict[str, float], document_vector: dict[str, float]) -> float:
    if not query_vector or not document_vector:
        return 0.0

    shared_tokens = set(query_vector) & set(document_vector)
    if not shared_tokens:
        return 0.0

    return sum(query_vector[token] * document_vector[token] for token in shared_tokens)


def retrieve_documents(
    query: str,
    *,
    preferred_documents: Iterable[RagDocument] = (),
    limit: int = 4,
) -> List[RagDocument]:
    query_tokens = set(tokenize(query))
    if not query_tokens and not normalize_text(query):
        return []

    rag_index = load_rag_index()
    query_vector = _compute_sparse_tfidf(list(query_tokens), rag_index["idf"])
    ranked: List[tuple[float, RagDocument]] = []
    seen_ids: set[str] = set()

    for document in preferred_documents:
        ranked.append((1000.0, document))
        seen_ids.add(document["id"])

    for document in rag_index["documents"]:
        if document["id"] in seen_ids:
            continue
        lexical_score = _score_document(query, query_tokens, document)
        vector_score = _cosine_similarity(query_vector, rag_index["vectors"].get(document["id"], {}))
        score = lexical_score + (vector_score * 20)
        if score > 0:
            ranked.append((score, document))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [document for _, document in ranked[:limit]]


def format_rag_context(documents: Iterable[RagDocument]) -> str | None:
    blocks = []
    for index, document in enumerate(documents, start=1):
        blocks.append(
            "\n".join(
                [
                    f"[{index}] {document['title']}",
                    f"Nguồn: {document['source_file']}",
                    document["text"],
                ]
            )
        )

    if not blocks:
        return None

    return "\n\n".join(blocks)


def build_rag_context(
    query: str,
    *,
    preferred_context: StructuredContext | None = None,
    limit: int = 4,
) -> tuple[str | None, List[JsonDict]]:
    preferred_documents: List[RagDocument] = []
    if preferred_context:
        preferred_document = build_structured_seed_document(preferred_context)
        if preferred_document:
            preferred_documents.append(preferred_document)

    documents = retrieve_documents(query, preferred_documents=preferred_documents, limit=limit)
    references = [
        {
            "title": document["title"],
            "domain": document["domain"],
            "source_file": document["source_file"],
        }
        for document in documents
        if document["source_file"] != "structured_context"
    ]
    return format_rag_context(documents), references
