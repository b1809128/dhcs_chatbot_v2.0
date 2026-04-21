import json
import math
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from typing import Iterable, List, TypedDict

from .config import INDEX_DIR
from .rag_documents import RagDocument, build_rag_documents
from .types import JsonDict


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

def _document_tokens(document: RagDocument) -> List[str]:
    return tokenize(" ".join([document["title"], document["text"], *document["keywords"]]))


def compute_sparse_tfidf(tokens: List[str], idf_map: dict[str, float]) -> dict[str, float]:
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


def build_tfidf_index(documents: Iterable[RagDocument]) -> RagIndex:
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
        document["id"]: compute_sparse_tfidf(_document_tokens(document), idf_map)
        for document in docs
    }
    return {
        "documents": docs,
        "idf": idf_map,
        "vectors": vectors,
    }


def serialize_index(index: RagIndex) -> JsonDict:
    return {
        "documents": index["documents"],
        "idf": index["idf"],
        "vectors": index["vectors"],
    }


def write_index(index: RagIndex) -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    path = INDEX_DIR / "rag_index.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(serialize_index(index), file, ensure_ascii=False, indent=2)


def load_index_from_disk() -> RagIndex | None:
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
    disk_index = load_index_from_disk()
    current_documents = list(build_rag_documents())

    if disk_index and len(disk_index["documents"]) == len(current_documents):
        return disk_index

    rebuilt_index = build_tfidf_index(current_documents)
    write_index(rebuilt_index)
    return rebuilt_index
