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

    def test_returns_pdf_document_for_specific_thong_tu(self):
        result = build_document_context("thông tư 62_2023")

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "pdf_document")
        self.assertEqual(result["so_hieu"], "62/2023/TT-BCA")
        self.assertEqual(
            result["file_url"],
            "/documents/thong_tu/thong_tu_62_2023.pdf",
        )

    def test_returns_quick_access_file_for_thong_tu_table(self):
        result = build_document_context("thông tư")

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "table")
        self.assertEqual(result["title"], "THÔNG TƯ")
        self.assertIn("Truy cập nhanh", result["columns"])
        self.assertTrue(any(row.get("file_url") for row in result["rows"]))

    def test_returns_pdf_document_for_luat_an_ninh_mang(self):
        result = build_document_context("luật an ninh mạng")

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "pdf_document")
        self.assertEqual(result["title"], "LUẬT")
        self.assertEqual(result["so_hieu"], "24/2018/QH14")
        self.assertEqual(
            result["file_url"],
            "/documents/law/luat_an_ninh_mang.pdf",
        )

    def test_returns_law_document_for_generic_luat_query(self):
        result = build_document_context("luật ban hành")

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "pdf_document")
        self.assertEqual(result["title"], "LUẬT")
        self.assertEqual(result["name"], "Luật An ninh mạng")
        self.assertEqual(
            result["file_url"],
            "/documents/law/luat_an_ninh_mang.pdf",
        )


if __name__ == "__main__":
    unittest.main()
