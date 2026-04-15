import unittest

from services.chatbot.document_context import build_document_context


class DocumentContextTests(unittest.TestCase):
    def test_returns_form_detail_for_don_xin_phep(self):
        result = build_document_context("đơn xin phép")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "BIỂU MẪU / ĐƠN")
        self.assertEqual(result["type"], "table")
        self.assertEqual(result["rows"][0]["ten"], "Đơn xin phép")

    def test_returns_documents_for_cong_van(self):
        result = build_document_context("công văn")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "CÔNG VĂN")
        self.assertTrue(len(result["rows"]) >= 1)


if __name__ == "__main__":
    unittest.main()
