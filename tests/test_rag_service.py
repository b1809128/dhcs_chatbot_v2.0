import unittest
from pathlib import Path

from services.chatbot.config import INDEX_DIR
from services.chatbot.rag_service import build_rag_context, build_rag_documents, load_rag_index


class RagServiceTests(unittest.TestCase):
    def test_builds_documents_from_internal_json(self):
        documents = build_rag_documents()

        self.assertGreater(len(documents), 10)
        self.assertTrue(any(document["source_file"] == "tuyen_sinh.json" for document in documents))
        self.assertTrue(any(document["source_file"] == "thu_vien.json" for document in documents))

    def test_builds_local_vector_index(self):
        index = load_rag_index()

        self.assertGreater(len(index["documents"]), 10)
        self.assertGreater(len(index["idf"]), 10)
        self.assertTrue((INDEX_DIR / "rag_index.json").exists())

    def test_retrieves_admission_context_for_text_queries(self):
        context, references = build_rag_context("điều kiện tuyển sinh văn bằng 2")

        self.assertIsNotNone(context)
        self.assertIn("Điều kiện chung", context)
        self.assertTrue(any(reference["source_file"] == "tuyen_sinh.json" for reference in references))

    def test_retrieves_library_context_for_text_queries(self):
        context, references = build_rag_context("mượn tối đa thư viện là bao nhiêu")

        self.assertIsNotNone(context)
        self.assertIn("Quy định mượn trả", context)
        self.assertTrue(any(reference["source_file"] == "thu_vien.json" for reference in references))


if __name__ == "__main__":
    unittest.main()
