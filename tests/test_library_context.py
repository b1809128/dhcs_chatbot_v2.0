import unittest

from services.chatbot.library_context import build_library_context


class LibraryContextTests(unittest.TestCase):
    def test_returns_opening_hours(self):
        result = build_library_context("giờ mở cửa thư viện")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "GIỜ MỞ CỬA THƯ VIỆN")
        self.assertEqual(result["type"], "table")
        self.assertTrue(any(row["muc"] == "Thứ hai đến thứ sáu" for row in result["rows"]))

    def test_returns_book_lookup_by_title(self):
        result = build_library_context("giáo trình luật hình sự")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "THÔNG TIN THƯ VIỆN")
        self.assertEqual(result["rows"][0]["ten_sach"], "Giáo trình Luật Hình sự")

    def test_returns_reading_room_materials(self):
        result = build_library_context("chỉ đọc tại chỗ")

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "TÀI LIỆU ĐỌC TẠI CHỖ")
        self.assertTrue(any("Hồ sơ vụ án mẫu" == row["ten_sach"] for row in result["rows"]))


if __name__ == "__main__":
    unittest.main()
