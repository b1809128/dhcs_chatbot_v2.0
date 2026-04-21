import math
from typing import Iterable, List

from .rag_documents import RagDocument
from .rag_index import compute_sparse_tfidf, load_rag_index, normalize_text, tokenize


def score_document(query: str, query_tokens: set[str], document: RagDocument) -> float:
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


def cosine_similarity(query_vector: dict[str, float], document_vector: dict[str, float]) -> float:
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
    query_vector = compute_sparse_tfidf(list(query_tokens), rag_index["idf"])
    ranked: List[tuple[float, RagDocument]] = []
    seen_ids: set[str] = set()

    for document in preferred_documents:
        ranked.append((1000.0, document))
        seen_ids.add(document["id"])

    for document in rag_index["documents"]:
        if document["id"] in seen_ids:
            continue
        lexical_score = score_document(query, query_tokens, document)
        vector_score = cosine_similarity(query_vector, rag_index["vectors"].get(document["id"], {}))
        score = lexical_score + (vector_score * 20)
        if score > 0:
            ranked.append((score, document))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [document for _, document in ranked[:limit]]
