import unittest
from importlib.util import find_spec
from unittest.mock import patch


if find_spec("flask") is not None:
    from app import app
else:
    app = None


@unittest.skipIf(app is None, "Flask is not installed in the current environment")
class AppAuthorizationTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_guest_can_only_access_admission_queries(self):
        response = self.client.post("/chat", json={"message": "lịch học lớp dths3"})

        self.assertEqual(response.status_code, 403)
        payload = response.get_json()
        self.assertIn("đăng nhập", payload["reply"].lower())
        self.assertIn("Chỉ tiêu tuyển sinh", payload["suggestions"])

    def test_guest_can_access_admission_queries(self):
        with patch(
            "services.chatbot.chat_service.ask_ollama",
            return_value="Thông tin tuyển sinh đang được hệ thống tổng hợp.",
        ):
            response = self.client.post("/chat", json={"message": "tuyển sinh"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "Thông tin tuyển sinh đang được hệ thống tổng hợp.")
        self.assertEqual(payload["source"], "ollama")
        self.assertIsNone(payload["data"])
        self.assertGreaterEqual(len(payload["references"]), 1)

    def test_guest_can_access_specific_admission_topics(self):
        response = self.client.post("/chat", json={"message": "hồ sơ nhập học"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "HỒ SƠ TUYỂN SINH")
        self.assertEqual(payload["source"], "structured")
        self.assertEqual(payload["data"]["type"], "list")
        self.assertEqual(payload["references"], [])

    def test_authenticated_user_can_access_internal_queries(self):
        login_response = self.client.post(
            "/login",
            data={
                "username": app.config["CHATBOT_USERNAME"],
                "password": app.config["CHATBOT_PASSWORD"],
            },
        )

        self.assertEqual(login_response.status_code, 302)

        response = self.client.post("/chat", json={"message": "lịch học lớp dths3"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "LỊCH HỌC")
        self.assertEqual(payload["source"], "structured")
        self.assertEqual(payload["references"], [])

    def test_authenticated_user_can_get_specific_pdf_document(self):
        self.client.post(
            "/login",
            data={
                "username": app.config["CHATBOT_USERNAME"],
                "password": app.config["CHATBOT_PASSWORD"],
            },
        )

        response = self.client.post("/chat", json={"message": "thông tư 62_2023"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["data"]["type"], "pdf_document")
        self.assertEqual(payload["source"], "structured")
        self.assertEqual(payload["references"], [])
        self.assertEqual(
            payload["data"]["file_url"],
            "/documents/thong_tu/thong_tu_62_2023.pdf",
        )

    def test_document_route_serves_pdf(self):
        response = self.client.get("/documents/thong_tu/thong_tu_62_2023.pdf")

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response.content_type)

    def test_law_document_route_serves_pdf(self):
        response = self.client.get("/documents/law/luat_an_ninh_mang.pdf")

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response.content_type)


if __name__ == "__main__":
    unittest.main()
