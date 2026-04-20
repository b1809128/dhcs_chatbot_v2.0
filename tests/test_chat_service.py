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
        self.assertIn("Chỉ tiêu tuyển sinh", result["suggestions"])
        self.assertIn("Bài thi VB2CA", result["suggestions"])
        mock_ask_ollama.assert_called_once()

    def test_keeps_structured_response_for_list_context(self):
        result = build_chat_response("hồ sơ nhập học")

        self.assertEqual(result["reply"], "HỒ SƠ TUYỂN SINH")
        self.assertEqual(result["data"]["type"], "list")
        self.assertEqual(result["source"], "structured")
        self.assertEqual(result["references"], [])

    def test_keeps_structured_response_for_pdf_documents(self):
        result = build_chat_response("thông tư 62_2023")

        self.assertEqual(result["data"]["type"], "pdf_document")
        self.assertEqual(result["source"], "structured")
        self.assertEqual(result["references"], [])

    def test_routes_generic_luat_query_to_document_context(self):
        result = build_chat_response("luật ban hành")

        self.assertEqual(result["data"]["type"], "pdf_document")
        self.assertEqual(result["data"]["title"], "LUẬT")
        self.assertEqual(result["data"]["name"], "Luật An ninh mạng")
        self.assertEqual(result["source"], "structured")
        self.assertEqual(result["references"], [])


if __name__ == "__main__":
    unittest.main()
