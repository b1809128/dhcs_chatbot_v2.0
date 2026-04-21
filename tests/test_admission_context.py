import unittest

from services.chatbot.admission_context import build_admission_context


class AdmissionContextTests(unittest.TestCase):
    def test_returns_admission_targets(self):
        result = build_admission_context("chỉ tiêu tuyển sinh")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "CHỈ TIÊU TUYỂN SINH")
        self.assertEqual(result["type"], "table")
        self.assertTrue(
            any(row["ma_truong"] == "CSS" and row["tong_chi_tieu"] == 100 for row in result["rows"])
        )

    def test_returns_admission_documents(self):
        result = build_admission_context("hồ sơ nhập học")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "HỒ SƠ TUYỂN SINH")
        self.assertEqual(result["type"], "list")
        self.assertTrue(any("Đơn đăng ký dự tuyển" in item for item in result["items"]))

    def test_returns_school_info(self):
        result = build_admission_context("mã trường css")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "THÔNG TIN TRƯỜNG")
        self.assertTrue(any(row["chi_tiet"] == "CSS" for row in result["rows"]))

    def test_returns_vb2ca_exam_documents(self):
        result = build_admission_context("bài thi vb2ca")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "BÀI THI ĐÁNH GIÁ")
        self.assertEqual(result["type"], "document_collection")
        self.assertEqual(len(result["documents"]), 4)
        self.assertTrue(
            any(document["file_url"] == "/documents/de_thi/CA1.pdf" for document in result["documents"])
        )

    def test_returns_van_bang_2_overview(self):
        result = build_admission_context("tuyển sinh văn bằng 2")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TUYỂN SINH VĂN BẰNG 2")
        self.assertEqual(result["type"], "table")
        self.assertTrue(any("VB2CA" in row["chi_tiet"] for row in result["rows"]))
        self.assertTrue(any("CSS" in row["chi_tiet"] for row in result["rows"]))

    def test_returns_unaccented_van_bang_2_overview(self):
        result = build_admission_context("tuyen sinh van bang 2")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TUYỂN SINH VĂN BẰNG 2")
        self.assertEqual(result["type"], "table")

    def test_returns_alias_van_bang_hai_overview(self):
        result = build_admission_context("tuyển sinh văn bằng hai")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TUYỂN SINH VĂN BẰNG 2")

    def test_returns_precheck_for_long_profile_question(self):
        result = build_admission_context("em tốt nghiệp CNTT loại khá, cao 1m62 có đăng ký CSS được không?")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "KIỂM TRA SƠ BỘ ĐIỀU KIỆN")
        self.assertEqual(result["type"], "table")
        self.assertTrue(any(row["tieu_chi"] == "Kết luận sơ bộ" for row in result["rows"]))
        self.assertTrue(any(row["tieu_chi"] == "Trường muốn đăng ký" and row["thong_tin"] == "CSS" for row in result["rows"]))

    def test_warns_for_lien_thong_van_bang_2_conflict(self):
        result = build_admission_context("liên thông văn bằng 2 có tuyển không")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "LƯU Ý MÂU THUẪN")
        self.assertIn("không tuyển sinh đối tượng trình độ liên thông", result["message"])

    def test_returns_professional_admission_views(self):
        cases = [
            ("tóm tắt tuyển sinh vb2ca", "TÓM TẮT TUYỂN SINH VB2CA 2026", "table"),
            ("timeline tuyển sinh", "TIMELINE TUYỂN SINH VB2CA 2026", "table"),
            ("checklist hồ sơ sơ tuyển", "CHECKLIST HỒ SƠ SƠ TUYỂN", "list"),
            ("so sánh phương thức tuyển sinh", "SO SÁNH PHƯƠNG THỨC TUYỂN SINH", "table"),
        ]

        for query, title, context_type in cases:
            with self.subTest(query=query):
                result = build_admission_context(query)
                self.assertIsNotNone(result)
                self.assertEqual(result["title"], title)
                self.assertEqual(result["type"], context_type)

    def test_filters_quota_by_school_code(self):
        result = build_admission_context("chỉ tiêu CSS")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "CHỈ TIÊU TUYỂN SINH")
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0]["ma_truong"], "CSS")

    def test_returns_health_standards(self):
        result = build_admission_context("tiêu chuẩn sức khỏe và chiều cao")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TIÊU CHUẨN SỨC KHỎE")
        self.assertEqual(result["type"], "list")
        self.assertTrue(any("BMI" in item for item in result["items"]))

    def test_returns_registration_steps(self):
        result = build_admission_context("lệ phí sơ tuyển")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "THỦ TỤC SƠ TUYỂN")
        self.assertEqual(result["type"], "table")
        self.assertTrue(any("100.000" in row["chi_tiet"] for row in result["rows"]))

    def test_returns_score_formula(self):
        result = build_admission_context("cách tính điểm xét tuyển")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "XÉT TUYỂN VÀ CÁCH TÍNH ĐIỂM")
        self.assertEqual(result["type"], "table")
        self.assertTrue(any("ĐXT" in row["chi_tiet"] for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
