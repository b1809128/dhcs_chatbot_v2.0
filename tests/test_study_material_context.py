import unittest

from services.chatbot.study_material_context import build_study_material_context


class StudyMaterialContextTests(unittest.TestCase):
    def test_returns_summary_context(self):
        result = build_study_material_context("tóm tắt giáo trình")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TÀI LIỆU NGHIỆP VỤ")
        self.assertTrue(any(row["chuc_nang"] == "Tóm tắt giáo trình" for row in result["rows"]))

    def test_returns_explanation_context(self):
        result = build_study_material_context("giải thích bài giảng")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TÀI LIỆU NGHIỆP VỤ")
        self.assertTrue(any("Giải thích" in row["chuc_nang"] or "Giải đáp" in row["chuc_nang"] for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
