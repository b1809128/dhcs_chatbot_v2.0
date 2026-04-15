import unittest

from services.chatbot.schedule_context import build_schedule_context


class ScheduleContextTests(unittest.TestCase):
    def test_returns_schedule_for_class_query(self):
        result = build_schedule_context("lịch học lớp dths3")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "LỊCH HỌC")
        self.assertEqual(result["type"], "table")
        self.assertTrue(any(row["lop"] == "DTHS3" for row in result["rows"]))

    def test_returns_exam_schedule_for_subject_query(self):
        result = build_schedule_context("lịch thi luật hình sự")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "LỊCH THI")
        self.assertEqual(result["rows"][0]["mon"], "Luật Hình sự")

    def test_returns_all_exam_schedule_for_generic_query(self):
        result = build_schedule_context("lịch thi")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "LỊCH THI")
        self.assertEqual(len(result["rows"]), 4)
        self.assertTrue(any(row["mon"] == "Kỹ thuật hình sự" for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
