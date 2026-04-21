import unittest
from unittest.mock import patch

from services.chatbot.chat_service import build_chat_response


class ChatServiceTests(unittest.TestCase):
    def test_returns_validation_message_for_blank_input(self):
        result = build_chat_response("   ")

        self.assertEqual(result["reply"], "Vui lòng nhập câu hỏi.")
        self.assertIsNone(result["data"])
        self.assertEqual(result["source"], "structured")
        self.assertEqual(result["suggestions"], [])
        self.assertEqual(result["references"], [])

    def test_keeps_structured_response_for_table_context(self):
        result = build_chat_response("giờ mở cửa thư viện")

        self.assertEqual(result["reply"], "GIỜ MỞ CỬA THƯ VIỆN")
        self.assertEqual(result["data"]["type"], "table")
        self.assertEqual(result["source"], "structured")
        self.assertEqual(len(result["suggestions"]), 4)
        self.assertIn("Mượn tối đa", result["suggestions"])

    @patch("services.chatbot.chat_service.ask_ollama", return_value="Thông tin tuyển sinh hiện đã được cập nhật.")
    def test_returns_more_suggestions_for_admission_queries(self, mock_ask_ollama):
        result = build_chat_response("tuyển sinh")

        self.assertEqual(result["reply"], "Thông tin tuyển sinh hiện đã được cập nhật.")
        self.assertIsNone(result["data"])
        self.assertEqual(result["source"], "ollama")
        self.assertGreaterEqual(len(result["references"]), 1)
        self.assertEqual(result["references"][0]["source_file"], "tuyen_sinh.json")
        self.assertGreaterEqual(len(result["suggestions"]), 8)
        self.assertIn("Chỉ tiêu theo từng trường", result["suggestions"])
        self.assertIn("Ngày thi 20/09/2026", result["suggestions"])
        mock_ask_ollama.assert_called_once()

    def test_keeps_structured_response_for_list_context(self):
        result = build_chat_response("hồ sơ nhập học")

        self.assertEqual(result["reply"], "HỒ SƠ TUYỂN SINH")
        self.assertEqual(result["data"]["type"], "list")
        self.assertEqual(result["source"], "structured")
        self.assertGreaterEqual(len(result["references"]), 1)
        self.assertEqual(result["references"][0]["title"], "HỒ SƠ TUYỂN SINH")

    def test_keeps_structured_response_for_pdf_documents(self):
        result = build_chat_response("thông tư 62_2023")

        self.assertEqual(result["data"]["type"], "pdf_document")
        self.assertEqual(result["source"], "structured")
        self.assertGreaterEqual(len(result["references"]), 1)
        self.assertEqual(
            result["references"][0]["file_url"],
            "/documents/thong_tu/thong_tu_62_2023.pdf",
        )

    def test_routes_generic_luat_query_to_document_context(self):
        result = build_chat_response("luật ban hành")

        self.assertEqual(result["data"]["type"], "pdf_document")
        self.assertEqual(result["data"]["title"], "LUẬT")
        self.assertEqual(result["data"]["name"], "Luật An ninh mạng")
        self.assertEqual(result["source"], "structured")
        self.assertGreaterEqual(len(result["references"]), 1)
        self.assertEqual(
            result["references"][0]["file_url"],
            "/documents/law/luat_an_ninh_mang.pdf",
        )

    def test_keeps_structured_response_for_document_collection(self):
        result = build_chat_response("bài thi vb2ca")

        self.assertEqual(result["data"]["type"], "document_collection")
        self.assertEqual(len(result["data"]["documents"]), 4)
        self.assertEqual(result["source"], "structured")
        self.assertEqual(len(result["references"]), 4)

    def test_keeps_structured_response_for_van_bang_2(self):
        result = build_chat_response("tuyển sinh văn bằng 2")

        self.assertEqual(result["reply"], "TUYỂN SINH VĂN BẰNG 2")
        self.assertEqual(result["data"]["type"], "table")
        self.assertEqual(result["source"], "structured")
        self.assertTrue(any("VB2CA" in row["chi_tiet"] for row in result["data"]["rows"]))
        self.assertGreaterEqual(len(result["suggestions"]), 8)
        self.assertIn("Đối tượng dự tuyển VB2CA", result["suggestions"])
        self.assertIn("Ngày thi 20/09/2026", result["suggestions"])

    def test_returns_so_tuyen_suggestions_for_registration_context(self):
        result = build_chat_response("hồ sơ sơ tuyển")

        self.assertEqual(result["reply"], "THỦ TỤC SƠ TUYỂN")
        self.assertEqual(result["source"], "structured")
        self.assertIn("Thủ tục đăng ký sơ tuyển", result["suggestions"][:3])
        self.assertIn("Lệ phí sơ tuyển", result["suggestions"][:5])

    def test_returns_precise_suggestions_for_professional_admission_views(self):
        cases = [
            (
                "tóm tắt tuyển sinh vb2ca",
                "TÓM TẮT TUYỂN SINH VB2CA 2026",
                ["Timeline tuyển sinh VB2CA 2026", "Checklist hồ sơ sơ tuyển", "So sánh phương thức tuyển sinh"],
            ),
            (
                "timeline tuyển sinh",
                "TIMELINE TUYỂN SINH VB2CA 2026",
                ["Hạn đăng ký 25/06/2026", "Ngày thi 20/09/2026", "Checklist hồ sơ sơ tuyển"],
            ),
            (
                "checklist hồ sơ sơ tuyển",
                "CHECKLIST HỒ SƠ SƠ TUYỂN",
                ["Thủ tục đăng ký sơ tuyển", "Lệ phí sơ tuyển", "Bằng tốt nghiệp và bảng điểm"],
            ),
            (
                "so sánh phương thức tuyển sinh",
                "SO SÁNH PHƯƠNG THỨC TUYỂN SINH",
                ["Phương thức 1 xét tuyển thẳng", "Phương thức 2 thi tuyển", "Cách tính điểm xét tuyển"],
            ),
            (
                "tài liệu và hành động tuyển sinh",
                "TÀI LIỆU VÀ HÀNH ĐỘNG TUYỂN SINH",
                ["Tải thông báo tuyển sinh", "Xem đề thi CA1", "Xem đề thi CA2"],
            ),
        ]

        for query, reply, expected_suggestions in cases:
            with self.subTest(query=query):
                result = build_chat_response(query)

                self.assertEqual(result["reply"], reply)
                self.assertEqual(result["source"], "structured")
                for suggestion in expected_suggestions:
                    self.assertIn(suggestion, result["suggestions"][:8])

    def test_returns_precise_suggestions_for_precheck_and_conflict(self):
        precheck = build_chat_response("em tốt nghiệp CNTT loại khá, cao 1m62 có đăng ký CSS được không?")

        self.assertEqual(precheck["reply"], "KIỂM TRA SƠ BỘ ĐIỀU KIỆN")
        self.assertIn("Kiểm tra sơ bộ điều kiện với tuổi, chiều cao, BMI", precheck["suggestions"][:3])
        self.assertIn("Checklist hồ sơ sơ tuyển", precheck["suggestions"][:8])

        conflict = build_chat_response("liên thông văn bằng 2 có tuyển không")

        self.assertEqual(conflict["reply"], "LƯU Ý MÂU THUẪN")
        self.assertIn("Điều kiện trình độ đào tạo", conflict["suggestions"][:3])
        self.assertIn("Kiểm tra sơ bộ điều kiện", conflict["suggestions"][:6])


if __name__ == "__main__":
    unittest.main()
