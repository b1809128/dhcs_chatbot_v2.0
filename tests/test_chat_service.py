import unittest

from services.chatbot.chat_service import build_chat_response


class ChatServiceTests(unittest.TestCase):
    def test_returns_validation_message_for_blank_input(self):
        result = build_chat_response("   ")

        self.assertEqual(result["reply"], "Vui lòng nhập câu hỏi.")
        self.assertIsNone(result["data"])

    def test_returns_structured_response_with_contextual_suggestions(self):
        result = build_chat_response("giờ mở cửa thư viện")

        self.assertEqual(result["reply"], "GIỜ MỞ CỬA THƯ VIỆN")
        self.assertEqual(result["data"]["title"], "GIỜ MỞ CỬA THƯ VIỆN")
        self.assertEqual(len(result["suggestions"]), 4)
        self.assertIn("Mượn tối đa", result["suggestions"])

    def test_returns_more_suggestions_for_admission_queries(self):
        result = build_chat_response("tuyển sinh")

        self.assertEqual(result["reply"], "TUYỂN SINH")
        self.assertEqual(result["data"]["title"], "TUYỂN SINH")
        self.assertGreaterEqual(len(result["suggestions"]), 8)
        self.assertIn("Chỉ tiêu tuyển sinh", result["suggestions"])
        self.assertIn("Bài thi VB2CA", result["suggestions"])


if __name__ == "__main__":
    unittest.main()
