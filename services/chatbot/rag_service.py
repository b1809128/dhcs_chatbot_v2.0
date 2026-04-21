from typing import Iterable, List

from .rag_documents import RagDocument, build_structured_seed_document
from .rag_retrieval import retrieve_documents
from .types import JsonDict, StructuredContext


__all__ = ["build_rag_context"]


def _format_rag_context(documents: Iterable[RagDocument]) -> str | None:
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
            "file_url": document.get("file_url", ""),
            "download_url": document.get("download_url", ""),
            "file_type": document.get("file_type", ""),
        }
        for document in documents
        if document["source_file"] != "structured_context"
    ]
    return _format_rag_context(documents), references
