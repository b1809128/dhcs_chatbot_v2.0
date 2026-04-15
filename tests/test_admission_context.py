import unittest

from services.chatbot.admission_context import build_admission_context


class AdmissionContextTests(unittest.TestCase):
    def test_returns_admission_targets(self):
        result = build_admission_context("chỉ tiêu tuyển sinh")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TUYỂN SINH")
        self.assertEqual(result["type"], "table")
        self.assertIn("Tổng chỉ tiêu năm 2026", result["rows"][0]["noi_dung"])

    def test_returns_admission_documents(self):
        result = build_admission_context("hồ sơ nhập học")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "HỒ SƠ TUYỂN SINH")
        self.assertEqual(result["type"], "list")
        self.assertTrue(any("Giấy báo nhập học" in item for item in result["items"]))

    def test_returns_school_info(self):
        result = build_admission_context("mã trường css")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "THÔNG TIN TRƯỜNG")
        self.assertTrue(any(row["chi_tiet"] == "CSS" for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
